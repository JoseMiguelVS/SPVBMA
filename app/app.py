import os
import psycopg2
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf=CSRFProtect()
    #----------------------conexion---------------------------------------------

def get_db_connection():

    try:
        conn = psycopg2.connect(host='localhost',
                                dbname='SPVBMAH',
                                user=os.environ['db_username'],
                                password=os.environ['db_password'])
        return conn
    except psycopg2.Error as error:
        print(f"error de conexion: {error}")
        return None
app.secret_key='chistosa'
@app.route("/")
def index():

    titulo = "orales"
    return render_template('index.html', titulo=titulo,) 
       
    #--------------------------------------inicio de sesion -------------------------------------
@app.route("/sesion")
def sesion():
    return render_template('sesion.html')
    #--------------------------------------------- CRUD usuarios ---------------------------------------
@app.route("/usuarios")
def usuarios():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT * FROM usuarios;')
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

@app.route("/usuarios/nuevo")
def usuario_nuevo():
    titulo = "Nuevo usuario"
    return render_template('usuario_nuevo.html', titulo=titulo)

@app.route('/usuarios/crear', methods=('GET', 'POST'))
def usuarios_crear():
    if request.method == 'POST':
        nombre_usuario= request.form['nombre_usuario']
        apellido_usuario= request.form['apellido_usuario']
        celular_usuario= request.form['celular_usuario']
        cargo= request.form['cargo']
        domicilio_usuario= request.form['domicilio_usuario']
        contrasenia= request.form['contrasenia']
        correo_electronico= request.form['correo_electronico']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO usuarios (nombre_usuario ,apellido_usuario, celular_usuario, cargo, domicilio_usuario,contrasenia,correo_electronico)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (nombre_usuario,apellido_usuario,celular_usuario,cargo,domicilio_usuario,contrasenia,correo_electronico))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Usuario agregado exitosamente!')

        return redirect(url_for('usuarios'))

    return redirect(url_for('usuario_nuevo'))

@app.route('/usuarios/<string:id>')
def usuarios_detalles(id):
    titulo="Detalles de usuario"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario={0}'.format(id))
    usuarios=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('usuario_detalles.html',titulo=titulo, usuarios=usuarios[0])

@app.route('/usuarios/editar/<string:id>')
def usuarios_editar(id):
    titulo="Editar Usuario"
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario={0}'.format(id))
    usuarios=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('usuarios_editar.html',titulo=titulo, usuarios=usuarios[0])

@app.route('/usuarios/editar/<string:id>', methods=['POST'])
def usuarios_actualizar(id):
    if request.method == 'POST':
        nombre_usuario= request.form['nombre_usuario']
        apellido_usuario= request.form['apellido_usuario']
        celular_usuario= request.form['celular_usuario']
        cargo= request.form['cargo']
        domicilio_usuario= request.form['domicilio_usuario']
        contrasenia= request.form['contrasenia']
        correo_electronico= request.form['correo_electronico']

        conn=get_db_connection()
        cur=conn.cursor()
        sql="UPDATE usuarios SET nombre_usuario=%s,apellido_usuario=%s,celular_usuario=%s,cargo=%s,domicilio_usuario=%s,contrasenia=%s,correo_electronico=%s WHERE id_usuario=%s"
        valores=(nombre_usuario,apellido_usuario,celular_usuario,cargo,domicilio_usuario,contrasenia, correo_electronico,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        flash("usuario editado correctamente")

    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar/<string:id>')
def usuarios_eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    flash('Usuario eliminado')
    return redirect(url_for('usuarios'))
    #------------------------ CRUD proveedores ------------------------------------------------------------
@app.route("/proveedores")
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
    return render_template('proveedores.html', proveedores = proveedores)

@app.route("/proveedores/nuevo")
def proveedor_nuevo():
    titulo = "Nuevo proveedor"
    return render_template('proveedor_nuevo.html', titulo=titulo)

@app.route('/proveedores/crear', methods=('GET', 'POST'))
def proveedores_crear():
    if request.method == 'POST':
        nombre_proveedor= request.form['nombre_proveedor']
        celular_proveedor= request.form['celular_proveedor']


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO proveedores (nombre_proveedor, celular_proveedor)'
                    'VALUES (%s, %s)',
                    (nombre_proveedor, celular_proveedor))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Proveedor agregado exitosamente!')

        return redirect(url_for('proveedores'))

    return redirect(url_for('proveedor_nuevo'))



    #--------------------------------CRUD prendas ----------------------------------------------------------

@app.route("/prendas")
def prendas():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT prendas.* , proveedores.nombre_proveedor FROM prendas LEFT JOIN proveedores ON prendas.nombre_prov = proveedores.id_proveedor ORDER BY id_prenda')
    print("--------------------")
    print("ESTO ES LA CONSULTA")
    prendas = cur.fetchall()
    for prenda in prendas:
        print("--------------------------")
        print(prenda)
        print("--------------------------")
    cur.close()
    conn.close()
    return render_template('prendas.html', prendas = prendas)

@app.route("/prendas/nuevo")
def prenda_nuevo():
    titulo = "Nueva prenda"
    return render_template('prenda_nuevo.html', titulo=titulo)

@app.route('/prendas/crear', methods=('GET', 'POST'))
def prendas_crear():
    if request.method == 'POST':
        tipo_prenda= request.form['tipo_prenda']
        talla_prenda= request.form['talla_prenda']
        color_prenda= request.form['color_prenda']
        precio_prenda= request.form['precio_prenda']
        marca_prenda= request.form['marca_prenda']
        stock= request.form['stock']
        codigo_prenda= request.form['codigo_prenda']
        nombre_prov= request.form['nombre_prov']



        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO prendas (tipo_prenda,talla_prenda,color_prenda,precio_prenda,marca_prenda,stock,codigo_prenda,nombre_prov)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (tipo_prenda,talla_prenda,color_prenda,precio_prenda,marca_prenda,stock,codigo_prenda,nombre_prov))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Prenda agregada exitosamente!')

        return redirect(url_for('prendas'))

    return redirect(url_for('prenda_nuevo'))

    #---------------------------------CRUD ventas ------------------------------------------------------------

@app.route("/ventas")
def ventas():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT ventas.*, prendas.tipo_prenda, usuarios.nombre_usuario FROM ventas LEFT JOIN prendas ON ventas.prenda = prendas.id_prenda LEFT JOIN usuarios ON ventas.usuario = usuarios.id_usuario ORDER BY ventas.id_venta;')
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
def venta_nuevo():
    titulo = "Nueva venta"
    return render_template('venta_nuevo.html', titulo=titulo)

@app.route('/ventas/crear', methods=('GET', 'POST'))
def ventas_crear():
    if request.method == 'POST':
        prenda= request.form['prenda']
        total_venta= request.form['total_venta']
        fecha_venta= request.form['fecha_venta']
        usuario= request.form['usuario']
    
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO ventas (prenda,total_venta,fecha_venta,usuario)'
                    'VALUES (%s, %s, %s, %s)',
                    (prenda,total_venta,fecha_venta,usuario))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Venta agregada exitosamente!')

        return redirect(url_for('ventas'))

    return redirect(url_for('venta_nuevo'))
    #--------------------------- CRUD del sistema de apartado ---------------------------------------------------

@app.route("/sApartado")
def sApartado():
    conn = get_db_connection()
    cur= conn.cursor()
    cur.execute('SELECT apartados.*, prendas.tipo_prenda FROM apartados LEFT JOIN prendas ON apartados.prenda = prendas.id_prenda  ORDER BY apartados.id_apartado;')
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

@app.route("/sApartado/nuevo")
def apartado_nuevo():
    titulo = "Nuevo apartado"
    return render_template('apartado_nuevo.html', titulo=titulo)

@app.route('/sApartado/crear', methods=('GET', 'POST'))
def apartados_crear():
    if request.method == 'POST':
        prenda= request.form['prenda']
        anticipo= request.form['anticipo']
        total_restante= request.form['total_restante']
        precio_final= request.form['precio_final']
        nombre_cliente= request.form['nombre_cliente']
        fecha_apartado= request.form['fecha_apartado']
        fecha_maxima= request.form['fecha_maxima']
    
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO apartados (prenda,anticipo,total_restante,precio_final,nombre_cliente,fecha_apartado,fecha_maxima)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (prenda,anticipo,total_restante,precio_final,nombre_cliente,fecha_apartado,fecha_maxima))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Venta agregada exitosamente!')

        return redirect(url_for('sApartado'))

    return redirect(url_for('apartado_nuevo'))
    
    #--------------------------------------------------------------------------------------- 
 
def pagina_no_encontrada(error):
    return render_template('404.html')

def acceso_no_autorizado(error):
    return redirect(url_for('sesion'))

if __name__ == '__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port=5000) 


# .venv\Scripts\activate
# python app\app.py run