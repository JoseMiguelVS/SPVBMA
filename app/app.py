import os
import uuid
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, url_for, redirect, request, flash, Blueprint, jsonify
from flask_wtf.csrf import CSRFProtect

from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from Models.ModelUser import ModuleUser
from Models.entities.user import User

app = Flask(__name__)
csrf=CSRFProtect() 

#-------------------------------conexion---------------------------------------------
def get_db_connection():
    try:
        conn = psycopg2.connect(host='localhost',
                                dbname='SPVBMA',
                                user=os.environ['db_username'],
                                password=os.environ['db_password'])
        return conn
    except psycopg2.Error as error:
        print(f"error de conexion: {error}")
        return None

#------------------------- Tiempo -------------------------
@app.template_filter('formatear_tiempo')
def formatear_tiempo(fecha_pasada):
    ahora = datetime.now()
    diferencia = relativedelta(ahora, fecha_pasada)

    if diferencia.years > 0:
        return f"Hace {diferencia.years} años"
    elif diferencia.years == 1:
        return f"Hace {diferencia.years} año"
    elif diferencia.months > 0:
        return f"Hace {diferencia.months} meses"
    elif diferencia.months == 1:
        return f"Hace {diferencia.months} mes"
    elif diferencia.days > 0:
        return f"Hace {diferencia.days} días"
    elif diferencia.days == 1:
        return f"Hace {diferencia.days} día"
    elif diferencia.hours > 0:
        return f"Hace {diferencia.hours} horas"
    elif diferencia.hours == 1:
        return f"Hace {diferencia.hours} hora"
    elif diferencia.minutes > 0:
        return f"Hace {diferencia.minutes} minutos"
    elif diferencia.minutes == 1:
        return f"Hace {diferencia.minutes} minuto"
    else:
        return "Hace unos segundos"
    
#--------------------------------Login------------------------------------------
Login_manager_app=LoginManager(app)
@Login_manager_app.user_loader
def load_user(idusuarios):
    return ModuleUser.get_by_id(get_db_connection(),idusuarios)

#--------------------------------IMAGEN------------------------------------------
def my_random_string(string_length=10):
    """Regresa una cadena aleatoria de la longitud de string_length."""
    random = str(uuid.uuid4()) # Conviente el formato UUID a una cadena de Python.
    random = random.upper() # Hace todos los caracteres mayusculas.
    random = random.replace("-","") # remueve el separador UUID '-'.
    return random[0:string_length] # regresa la cadena aleatoria.

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ruta_usuarios=app.config['UPLOAD_FOLDER']='./app/static/img/uploads/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#-------------------------------- SECRET KEY ---------------------------
app.secret_key='chistosa'

#----------------------------------RUTAS---------------------------------------
@app.route("/")
def login():
    return render_template('sesion.html')

@app.route("/index")
@login_required
def index():
    return render_template('index.html')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

def allowed_username(nombre_usuario):
    # Define el patrón de la expresión regular para letras y números sin espacios ni caracteres especiales
    pattern = re.compile(r'^[a-zA-Z0-9]+$')
    # Comprueba si el nombre de usuario coincide con el patrón
    if pattern.match(nombre_usuario):
        return True
    else:
        return False

#------------------------------------------consulta de prendas-------------------------------------------
def lista_prendas():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute("SELECT * FROM prenda ORDER BY id_prenda")
    prendas=cur.fetchall()
    cur.close()
    conn.close()
    return prendas

# ------------------------------------------consulta de categorias-----------------------------------------------
def lista_categorias():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM categoria ORDER BY id_categoria ASC ')
    categorias=cur.fetchall()
    cur.close()
    conn.close()
    return categorias

# --------------------------------------consulta de roles-----------------------------------------------------------
def lista_rol():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM roles ORDER BY id_rol ASC ')
    roles=cur.fetchall()
    cur.close()
    conn.close()
    return roles

#-------------------------------------consulta de tallas---------------------------------------------------------------
def lista_tallas():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM tallas ORDER BY id_tallas ASC')
    tallas=cur.fetchall()
    cur.close()
    conn.close()
    return tallas

#-------------------------------------consulta de colores---------------------------------------------------------------
def lista_colores():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM colores ORDER BY id_color ASC')
    colores=cur.fetchall()
    cur.close()
    conn.close()
    return colores

#----------------------------------consulta de marcas------------------------------------------------------------------
def lista_marcas():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM marcas ORDER BY id_marca ASC')
    marcas=cur.fetchall()
    cur.close()
    conn.close()
    return marcas

#---------------------------------------consulta de proveedor-----------------------------------------------------
def lista_proveedores():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY id_proveedores ASC')
    proveedores=cur.fetchall()
    cur.close()
    conn.close()
    return proveedores

#-------------------------------------------consulta de detalles apartado--------------------------------------
def detapar():
    conn = get_db_connection()  
    cur = conn.cursor()
    cur.execute('SELECT * FROM apade ORDER BY categoria ASC;')
    detapas = cur.fetchall()
    cur.close()
    conn.close()
    return detapas

#-----------------------------------------------------PAGINADOR---------------------------------------------------------
def paginador(sql_count,sql_lim,in_page,per_pages):
    page = request.args.get('page', in_page, type=int)
    per_page = request.args.get('per_page', per_pages, type=int)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(sql_count)
    total_items = cursor.fetchone()['count']

    cursor.execute(sql_lim, (per_page, offset))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_items + per_page - 1) // per_page

    return items, page, per_page, total_items, total_pages

#--------------------------------------------------------inicio de sesion --------------------------------------------

@app.route('/loguear', methods=('GET','POST'))
def loguear():
    if request.method == 'POST':
        nombre_usuario=request.form['nombre_usuario']
        contrasenia=request.form['contrasenia']
        user=User(0,nombre_usuario,contrasenia,None,None)
        loged_user=ModuleUser.login(get_db_connection(),user)

        if loged_user!= None:
            if loged_user.contrasenia:
                login_user(loged_user)
                return redirect(url_for('dashboard'))
            else:
                flash('Nombre de usuario y/o contraseña incorrecta.')
                return redirect(url_for('login'))
        else:
            flash('Nombre de usuario y/o contraseña incorrecta.')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#------------------------------------------------- CRUD usuarios --------------------------------------------------------
@app.route("/usuarios")
@login_required
def usuarios():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM usuarios ORDER BY id_usuario;')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    usuarios = cur.fetchall()
    for usuario in usuarios:
        print("--------------------------")
        print(usuario)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('usuarios.html',usuarios=usuarios)

@app.route("/usuarios/papelera")
@login_required
def usuarios_papelera():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM usuarios ORDER BY id_usuario;')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    usuarios = cur.fetchall()
    for usuario in usuarios:
        print("--------------------------")
        print(usuario)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('usuarios_papelera.html',usuarios=usuarios)

@app.route("/usuarios/nuevo")
@login_required
def usuario_nuevo():
    titulo = "Nuevo usuario"
    return render_template('usuario_nuevo.html', titulo=titulo, roles=lista_rol())

@app.route('/usuarios/crear', methods=('GET', 'POST'))
@login_required
def usuarios_crear():
    if request.method == 'POST':
        nombre_usuario= request.form['nombre_usuario']
        if allowed_username(nombre_usuario):
            apellido_paterno= request.form['apellido_paterno']
            apellido_materno= request.form['apellido_materno']
            celular_usuario= request.form['celular_usuario']
            domicilio_usuario= request.form['domicilio_usuario']
            contrasenia= request.form['contrasenia']
            Pass= generate_password_hash(contrasenia)
            correo_electronico= request.form['correo_electronico']
            rol= request.form['id_rol']
            estado = True
            creado = datetime.now()
            editado =datetime.now() 
            imagen = request.files['foto']
            filename = None  # Inicializar filename para evitar el error de variable no definida

            if imagen and allowed_file(imagen.filename):
                # Verificar si el archivo con el mismo nombre ya existe
                # Crear un nombre dinámico para la foto de perfil con el nombre del alumno y una cadena aleatoria
                cadena_aleatoria = my_random_string(10)
                filename = apellido_paterno + "" + apellido_materno + "" + nombre_usuario + "" + str(creado)[:10] + "" + cadena_aleatoria + "_" + secure_filename(imagen.filename)
                file_path = os.path.join(ruta_usuarios, filename)
                if os.path.exists(file_path):
                    flash('Error: ¡Un archivo con el mismo nombre ya existe! Intente renombrar su archivo.')
                    return redirect(url_for('usuarios'))
                # Guardar el archivo y registrar en la base de datos
            imagen.save(file_path)

            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            sql_validar="SELECT COUNT(*) FROM usuarios WHERE correo_electronico = '{}'".format(correo_electronico)
            cur.execute(sql_validar)
            existe = cur.fetchone()['count']
            if existe:
                cur.close()
                conn.close()
                flash('ERROR: El correo seleccionado ya existe. intente con otro.')
                return redirect(url_for('usuario_nuevo'))
            else:
                sql="INSERT INTO usuarios(nombre_usuario, apellido_paterno, apellido_materno, celular_usuario, domicilo_usuario, contrasenia, correo_electronico, rol, estado, creado, editado, foto) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                valores=(nombre_usuario,apellido_paterno,apellido_materno,celular_usuario,domicilio_usuario,Pass,correo_electronico,rol,estado,creado,editado, filename)
                cur.execute(sql,valores)
                conn.commit()
                cur.close()
                conn.close()
                flash('¡Usuario agregado exitosamente!')
                return redirect(url_for('usuarios'))
        else:
            flash('Error: El correo de usuario no cumple con las características. Intente con otro.')
            return redirect(url_for('usuario_nuevo'))
    return redirect(url_for('usuario_nuevo'))

@app.route('/usuarios/<string:id>')
@login_required
def usuarios_detalles(id):
    titulo="Detalles de usuario"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM usuarios INNER JOIN roles ON roles.id_rol=usuarios.rol WHERE id_usuario={0}'.format(id))
    usuarios=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('usuario_detalles.html',titulo=titulo, usuarios=usuarios[0])

@app.route('/usuarios/papelera/<string:id>')
@login_required
def usuarios_detallesRes(id):
    titulo="Detalles de usuario"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM usuarios INNER JOIN roles  ON roles.id_rol=usuarios.rol WHERE id_usuario={0}'.format(id))
    usuarios=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('usuario_detallesRes.html',titulo=titulo, usuarios=usuarios[0])

@app.route('/usuarios/restaurar/<string:id>')
@login_required
def usuarios_restaurar(id):
    estado = True
    editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    #sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
    sql="UPDATE usuarios SET  estado=%s,editado=%s WHERE id_usuario=%s"
    valores=(estado,editado,id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Usuario restaurado')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/editar/<string:id>')
@login_required
def usuarios_editar(id):
    if current_user.rol == 1:
        titulo="Editar Usuario"
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id_usuario={0}'.format(id))
        usuarios=cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('usuarios_editar.html',titulo=titulo, usuarios=usuarios[0],roles=lista_rol())
    else:
        return redirect(url_for('usuarios'))

@app.route('/usuarios/editar/<string:id>', methods=['POST'])
@login_required
def usuarios_actualizar(id):
    if request.method == 'POST':
        nombre_usuario= request.form['nombre_usuario']
        apellido_paterno= request.form['apellido_paterno']
        apellido_materno= request.form['apellido_materno']
        celular_usuario= request.form['celular_usuario']
        domicilio_usuario= request.form['domicilio_usuario']
        contrasenia= request.form['contrasenia']
        correo_electronico= request.form['correo_electronico']
        rol= request.form['id_rol']
        editado =datetime.now() 

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE public.usuarios SET nombre_usuario=%s, apellido_paterno=%s, apellido_materno=%s, celular_usuario=%s, domicilo_usuario=%s, contrasenia=%s, correo_electronico=%s, rol=%s, editado=%s WHERE id_usuario=%s"
        valores=(nombre_usuario,apellido_paterno,apellido_materno,celular_usuario,domicilio_usuario,contrasenia, correo_electronico,rol,editado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash("usuario editado correctamente")
    return redirect(url_for('usuarios'))

@app.route('/usuarios/editar/foto/<string:id>', methods=['POST'])
@login_required
def usuarios_actualizar_foto(id):
    if request.method == 'POST':
        imagen=request.files['foto']
        nombre_usuario= request.form['nombre_usuario']
        apellido_paterno= request.form['apellido_paterno']
        apellido_materno= request.form['apellido_materno']
        foto_anterior = request.form['anterior']
        foto_anterior = os.path.join(ruta_usuarios,foto_anterior)
        editado = datetime.now()

        if imagen and allowed_file(imagen.filename):
                # Verificar si el archivo con el mismo nombre ya existe
                # Crear un nombre dinámico para la foto de perfil con el nombre del alumno y una cadena aleatoria
                cadena_aleatoria = my_random_string(10)
                filename = apellido_paterno + "" + apellido_materno + "" + nombre_usuario + "" + str(editado)[:10] + "" + cadena_aleatoria + "_" + secure_filename(imagen.filename)
                file_path = os.path.join(ruta_usuarios, filename)
                if os.path.exists(file_path):
                    flash('Error: ¡Un archivo con el mismo nombre ya existe! Intente renombrar su archivo.')
                    return redirect(url_for('usuarios'))
                # Guardar el archivo y registrar en la base de datos
                imagen.save(file_path)

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE usuarios SET editado=%s, foto=%s WHERE id_usuario=%s"
        valores=(editado,filename,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close() 

        #Eliminar foto de perfil antigua
        if request.form['anterior'] != "":
            if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)

            flash('¡Foto de perfil actualizada exitosamente!')
            return redirect(url_for('usuarios_actualizar', id=id))
        else:
            flash('Error: ¡Extensión de archivo invalida! Intente con una imagen valida PNG, JPG o JPEG')
            return redirect(url_for('usuarios_actualizar', id=id))

    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar/<string:id>')
@login_required
def usuarios_eliminar(id):
    if current_user.rol == 1:
        estado=False
        editado = datetime.now()
        conn = get_db_connection()
        cur = conn.cursor()
        #sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
        sql="UPDATE usuarios SET  estado=%s, editado=%s WHERE id_usuario=%s"
        valores=(estado,editado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Usuario eliminado')
        return redirect(url_for('usuarios'))
    else:
        return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar/foto/<string:foto>/<string:id>')
@login_required
def usuarios_eliminar_foto(foto,id):
    if current_user.rol == 1:
        foto_anterior = os.path.join(ruta_usuarios,foto)
        editado = datetime.now()
        conn = get_db_connection()
        cur = conn.cursor()
        #sql="DELETE FROM alumnos WHERE id_alumno={0}".format(id)
        sql="UPDATE usuarios SET foto=%s, editado=%s WHERE id_usuario=%s"
        valores=("",editado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        #Eliminar foto de perfil antigua
        print(foto_anterior)
        if foto != "":
            if os.path.exists(foto_anterior):
                os.remove(foto_anterior)
                flash('¡Foto eliminada correctamente!')
                return redirect(url_for('usuarios_actualizar', id=id))
        else:
            flash('Error: ¡No se puede ejecutar esta acción!')
            return redirect(url_for('usuarios_actualizar', id=id))
    else:
        return redirect(url_for('usuarios'))

#---------------------------------------- CRUD proveedores ------------------------------------------------------------
@app.route("/proveedores")
@login_required
def proveedores():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM proveedores;')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    proveedores = cur.fetchall()
    for proveedor in proveedores:
        print("--------------------------")
        print(proveedor)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('proveedores.html',proveedores=proveedores)

@app.route("/proveedores/nuevo")
@login_required
def proveedores_nuevo():
    titulo = "Nuevo proveedor"
    return render_template('proveedores_nuevo.html', titulo=titulo)

@app.route('/proveedores/crear', methods=('GET', 'POST'))
@login_required
def proveedores_crear():
    if request.method == 'POST':
        nombre_proveedor= request.form['nombre']
        celular_proveedor= request.form['celular']
        estado=True
        creado= datetime.now()
        modificado = datetime.now()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO proveedores (nombre_proveedor , celular_proveedor, estado, creado, modificado)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (nombre_proveedor,celular_proveedor, estado, creado, modificado))
        conn.commit()
        cur.close()
        conn.close()
        flash('proveedor agregado exitosamente!')
        return redirect(url_for('proveedores'))
    return redirect(url_for('proveedores_nuevo'))

@app.route('/proveedores/<string:id>')
@login_required
def proveedores_detalles(id):
    titulo="Detalles de proveedor"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM proveedores WHERE id_proveedores={0}'.format(id))
    proveedores=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('proveedores_detalles.html',titulo=titulo, proveedores=proveedores[0])

@app.route('/proveedores/detalles/<string:id>')
@login_required
def proveedores_detallesRes(id):
    titulo="Detalles de proveedor"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM proveedores WHERE id_proveedores={0}'.format(id))
    proveedores=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('proveedores_detallesRes.html',titulo=titulo, proveedores=proveedores[0])

@app.route('/proveedores/editar/<string:id>')
@login_required
def proveedores_editar(id):
    if current_user.rol == 1:
        titulo="Editar Proveedor"
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute('SELECT * FROM proveedores WHERE id_proveedores={0}'.format(id))
        proveedores=cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('proveedores_editar.html',titulo=titulo, proveedor=proveedores[0])
    else:
        return redirect(url_for('proveedores'))

@app.route('/proveedores/editar/<string:id>', methods=['POST'])
@login_required
def proveedores_actualizar(id):
    if request.method == 'POST':
        nombre_proveedor= request.form['nombre_proveedor']
        celular_proveedor= request.form['celular_proveedor']
        estado=True
        creado= datetime.now()
        modificado = datetime.now()

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE proveedores SET nombre_proveedor=%s,celular_proveedor=%s, estado=%s,creado=%s,modificado=%s WHERE id_proveedores=%s"
        valores=(nombre_proveedor,celular_proveedor, estado, creado, modificado, id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash("proveedor editado correctamente")
    return redirect(url_for('proveedores'))

@app.route('/proveedores/eliminar/<string:id>')
@login_required
def proveedor_eliminar(id):
    if current_user.rol == 1:
        estado=False
        modificado= datetime.now()
        conn = get_db_connection()
        cur = conn.cursor()
        #sql="DELETE FROM proveedores WHERE id_proveedores={0}".format(id)
        sql="UPDATE proveedores SET estado=%s, modificado=%s WHERE id_proveedores=%s"
        valores=(estado,modificado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Proveedor eliminado')
        return redirect(url_for('proveedores'))
    else:
        return redirect(url_for('proveedores'))

@app.route('/proveedores/eliminar/papelera/<string:id>')
@login_required
def proveedor_restaurar(id):
    estado=True
    modificado= datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    #sql="DELETE FROM proveedores WHERE id_proveedores={0}".format(id)
    sql="UPDATE proveedores SET estado=%s, modificado=%s WHERE id_proveedores=%s"
    valores=(estado,modificado,id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Proveedor restaurado')
    return redirect(url_for('proveedores'))

@app.route("/proveedores/papelera")
@login_required
def proveedor_papelera():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY id_proveedores')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    proveedores = cur.fetchall()
    for proveedor in proveedores:
        print("--------------------------")
        print(proveedor)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('proveedores_papelera.html',proveedores=proveedores)  
  
#------------------------------------------CRUD prendas ----------------------------------------------------------
@app.route("/prendas")
@login_required
def prendas():
    sql_count= 'SELECT COUNT(*) FROM prendas WHERE estado=true;'
   # sql_lim='SELECT prendas.id_prenda, prendas.codigo_producto, proveedores.nombre_proveedor, categoria.categoria, marcas.nombre_marca, prendas.estado, prendas.creado, prendas.modificado, colores.color, tallas.talla, prendas.precio_prenda FROM prendas JOIN proveedores ON prendas.nombre_proveedor = proveedores.id_proveedores JOIN categoria ON prendas.categoria_prenda = categoria.id_categoria JOIN marcas ON prendas.marca_prenda = marcas.id_marca JOIN colores ON prendas.color_prenda = colores.id_color JOIN tallas ON prendas.talla_prenda = tallas.id_tallas ORDER BY id_prenda DESC LIMIT %s OFFSET %s;'
    sql_lim='SELECT * FROM public.prendas_vista WHERE estado=true ORDER BY id_prenda DESC LIMIT %s OFFSET %s;'
    paginado = paginador(sql_count,sql_lim,1,1)
    return render_template('prendas.html',
                           prendas=paginado[0],
                           page=paginado[1],
                           per_page=paginado[2],
                           total_items=paginado[3],
                           total_pages=paginado[4])

@app.route("/prendas/nuevo")
@login_required
def prenda_nuevo():
    titulo = "Nueva prenda"
    return render_template('prenda_nuevo.html', titulo=titulo,categorias=lista_categorias(),tallas=lista_tallas(),colores=lista_colores(),marcas=lista_marcas(),proveedores=lista_proveedores())

@app.route('/prendas/<string:id>')
@login_required
def prendas_detalles(id):
    titulo="Detalles de prendas"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM public.prenda WHERE id_prenda={0}'.format(id))
    prendas=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('prendas_detalles.html',titulo=titulo, prendas=prendas[0])

@app.route('/prendas/detalles/<string:id>')
@login_required
def prendas_detallesRes(id):
    titulo="Detalles de prendas"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM public.prenda WHERE id_prenda={0}'.format(id))
    prendas=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('prendas_detallesRes.html',titulo=titulo, prendas=prendas[0])

@app.route('/prendas/crear', methods=('GET', 'POST'))
@login_required
def prendas_crear():
    if request.method == 'POST':
        codigo_producto= request.form['codigo_prod']
        nombre_proveedor= request.form['nombre_prov']
        categoria_prenda= request.form['categoria_prenda']
        marca_prenda= request.form['marca_prenda']
        estado= True
        creado= datetime.now()
        modificado= datetime.now()
        color_prenda= request.form['color_prenda']
        talla_prenda= request.form['talla_prenda']
        precio_prenda= request.form['precio_prenda']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO prendas(codigo_producto, nombre_proveedor, categoria_prenda, marca_prenda, estado, creado, modificado, color_prenda, talla_prenda, precio_prenda)'
	                'VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                    (codigo_producto, nombre_proveedor, categoria_prenda, marca_prenda, estado, creado, modificado, color_prenda, talla_prenda, precio_prenda))
        conn.commit()
        cur.close()
        conn.close()
        flash('¡Prenda agregada exitosamente!')
        return redirect(url_for('prendas'))
    return redirect(url_for('prenda_nuevo'))

@app.route('/prendas/editar/<string:id>')
@login_required
def prendas_editar(id):
    if current_user.rol == 1:
        titulo="Editar Prenda"
        conn=get_db_connection()
        cur=conn.cursor()
        cur.execute('SELECT * FROM prendas WHERE id_prenda={0}'.format(id))
        prendas=cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return render_template('prendas_editar.html',titulo=titulo,prendas=prendas[0],colores=lista_colores())
    else:
        return redirect(url_for('prendas'))

@app.route('/prendas/editar/<string:id>',methods=['POST'])
@login_required
def prendas_actualizar(id):
    if request.method == 'POST':
        codigo_producto= request.form['codigo_prod']
        modificado= datetime.now()
        color_prenda= request.form['color_prenda']
        precio_prenda= request.form['precio_prenda']

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE public.prendas SET codigo_producto=%s, modificado=%s, color_prenda=%s, precio_prenda=%s WHERE id_prenda=%s;"
        valores=(codigo_producto,modificado,color_prenda,precio_prenda,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash("Prenda actualizada")
    return redirect(url_for('prendas'))

@app.route("/prenda/papelera")
@login_required
def prenda_papelera():
    sql_count= 'SELECT COUNT(*) FROM prendas WHERE estado=false;'
   # sql_lim='SELECT prendas.id_prenda, prendas.codigo_producto, proveedores.nombre_proveedor, categoria.categoria, marcas.nombre_marca, prendas.estado, prendas.creado, prendas.modificado, colores.color, tallas.talla, prendas.precio_prenda FROM prendas JOIN proveedores ON prendas.nombre_proveedor = proveedores.id_proveedores JOIN categoria ON prendas.categoria_prenda = categoria.id_categoria JOIN marcas ON prendas.marca_prenda = marcas.id_marca JOIN colores ON prendas.color_prenda = colores.id_color JOIN tallas ON prendas.talla_prenda = tallas.id_tallas ORDER BY id_prenda DESC LIMIT %s OFFSET %s;'
    sql_lim='SELECT * FROM public.prendas_vista WHERE estado=false ORDER BY id_prenda DESC LIMIT %s OFFSET %s;'
    paginado = paginador(sql_count,sql_lim,1,1)
    return render_template('prendas_papelera.html',
                           prendas=paginado[0],
                           page=paginado[1],
                           per_page=paginado[2],
                           total_items=paginado[3],
                           total_pages=paginado[4])

@app.route('/prendas/eliminar/<string:id>')
@login_required
def prendas_eliminar(id):
    if current_user.rol == 1:
        estado = False
        modificado   = datetime.now()
        conn = get_db_connection()
        cur = conn.cursor()
        #sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
        sql="UPDATE prendas SET  estado=%s,modificado=%s WHERE id_prenda=%s"
        valores=(estado,modificado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash('Prenda eliminada eliminado')
        return redirect(url_for('prendas'))
    else:
        return redirect(url_for('prendas'))

@app.route('/prendas/restaurar/<string:id>')
@login_required
def prendas_restaurar(id):
    estado = True
    modificado   = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    #sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
    sql="UPDATE prendas SET  estado=%s,modificado=%s WHERE id_prenda=%s"
    valores=(estado,modificado,id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('Prenda restaurada')
    return redirect(url_for('prendas'))

#---------------------------------CRUD ventas ------------------------------------------------------------

@app.route("/ventas")
@login_required
def ventas():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM ventas')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    ventas = cur.fetchall()
    for venta in ventas:
        print("--------------------------")
        print(venta)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

@app.route("/ventas/nuevo")
@login_required
def venta_nuevo():
    titulo = "Nueva venta"
    return render_template('venta_nuevo.html', titulo=titulo)

@app.route('/ventas/crear', methods=('GET', 'POST'))
@login_required
def ventas_crear():
    if request.method == 'POST':
        detven= request.form['detven']
        usuario= request.form['usuario']
        fecha_creacion = datetime.now()
    
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO ventas (detven,usuario,fecha_creacion)'
                    'VALUES (%s, %s, %s)',
                    (detven,usuario,fecha_creacion))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Venta agregada exitosamente!')
        return redirect(url_for('ventas'))
    return redirect(url_for('venta_nuevo'))

@app.route('/ventas/<string:id>')
@login_required
def venta_detallado(id):
    titulo = "Vista ventas"
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM ventas WHERE id_venta={0}'.format(id))
    ventas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('venta_detallado.html',titulo = titulo, ventas = ventas[0])

@app.route('/ventas/editar/<string:id>')
@login_required
def venta_editar(id):
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM ventas WHERE id_venta={0}'.format(id))
    ventas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('venta_editar.html',ventas = ventas[0])

@app.route('/ventas/actualizar/<string:id>', methods=['POST'])
@login_required
def venta_actualizar(id):
    if request.method == 'POST':
        detven= request.form['detven']
        usuario= request.form['usuario']
  
        conn = get_db_connection()
        cur = conn.cursor()
        sql = "UPDATE ventas SET detven=%s, usuario=%s WHERE id_venta=%s"
        valores = (detven,usuario,id)
        cur.execute (sql,valores)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Venta editada exitosamente!')
    return redirect(url_for('ventas'))

@app.route('/ventas/eliminar/<string:id>')
@login_required
def ventas_eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM ventas WHERE id_venta={0}".format(id)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Alumno  eliminado correctamente!')
    return redirect(url_for('ventas'))

#--------------------------- CRUD de sistema de apartado ---------------------------------------------------

@app.route("/sApartado")
@login_required
def sApartado():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM public.apartados ')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    apartados = cur.fetchall()
    for apartado in apartados:
        print("--------------------------")
        print(apartado)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('sApartado.html', apartados=apartados)

@app.route("/sApartado/papelera")
@login_required
def apartado_papelera():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM public.apartado  ')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    apartados = cur.fetchall()
    for apartado in apartados:
        print("--------------------------")
        print(apartado)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('apartado_papelera.html', apartados=apartados)

@app.route("/sApartado/nuevo")
@login_required
def apartado_nuevo():
    titulo = "Nuevo apartado"
    return render_template('apartado_nuevo.html', titulo=titulo, prendas=lista_prendas())

@app.route('/sApartado/crear', methods=('GET', 'POST'))
@login_required
def apartados_crear():
    if request.method == 'POST':
        anticipo = request.form['anticipo']
        precio_final = request.form['precio_final']
        nombre_cliente = request.form['nombre_cliente']
        detapa= request.form ['detapa']
        creado = datetime.now()
        fecha_apartado = request.form['fecha_apartado']
        fecha_limite = request.form['fecha_limite']
        cantidad=request.form['']
        editado= datetime.now()
        activo = True

        conn = get_db_connection()  
        cur = conn.cursor()
        sum=('SELECT count(prendas) FROM prendas')
        cur.execute('INSERT INTO apartados (anticipo, precio_final,detapa, nombre_cliente, creado, fecha_apartado, fecha_limite,editado,  activo)'
                    'VALUES (%s, %s,%s, %s, %s, %s, %s,%s,%s)',
                    (anticipo, precio_final,detapa, nombre_cliente, creado, fecha_apartado, fecha_limite,editado, activo))
        cur.execute('INSERT INTO detalles_apartado (prenda,cantidad)'
                    'VALUES (%s,%s)',
                    (detapa,cantidad))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Venta agregada exitosamente!')
        return redirect(url_for('sApartado'))
    return redirect(url_for('apartado_nuevo'))

@app.route('/sApartado/<string:id>')
@login_required
def apartado_detalle(id):
    titulo="Detalles de apartado"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM apartado WHERE id_apartado={0}'.format(id))
    apartados=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('apartado_detalle.html',titulo=titulo, apartados=apartados[0])

@app.route('/sApartado/editar/<string:id>')
@login_required
def apartado_editar(id):
    titulo="Editar apartado"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM apartados WHERE id_apartado={0}'.format(id))
    apartados=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('apartado_editar.html',titulo=titulo, apartados=apartados[0], detapas=detapar())

@app.route('/sApartado/editar/<string:id>', methods=['POST'])
@login_required
def apartado_actualizar(id):
  if request.method == 'POST':
        anticipo = request.form['anticipo']
        precio_final = request.form['precio_final']
        nombre_cliente = request.form['nombre_cliente']
        detapa= request.form ['detapa']
        fecha_apartado = request.form['fecha_apartado']
        fecha_limite = request.form['fecha_limite']
        editado= datetime.now()
        activo = True

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE apartados SET anticipo=%s,precio_final=%s,nombre_cliente=%s,detapa=%s,fecha_apartado=%s,fecha_limite=%s,editado=%s, activo=%s WHERE id_apartado=%s"
        valores=(anticipo, precio_final, nombre_cliente,detapa, fecha_apartado, fecha_limite,editado, activo,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash("apartado editado correctamente")
        return redirect(url_for('sApartado'))

@app.route('/sApartado/eliminar/<string:id>')
@login_required
def apartado_eliminar(id):
    activo = False
    conn = get_db_connection()
    cur = conn.cursor()
    sql="UPDATE apartados SET activo=%s WHERE id_apartado=%s"
    valores=(activo,id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Apartado eliminado correctamente!')
    return redirect(url_for('sApartado'))
    
    #--------------------------------------------------------------------------------------- 

#-------------------------------errores------------------------------------
def pagina_no_encontrada(error):
    return render_template('404.html')

def acceso_no_autorizado(error):
    return redirect(url_for('login'))

if __name__ == '__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port=5000) 
#todos los derechos reservados