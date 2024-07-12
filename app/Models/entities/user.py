from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):

    def get_id(self):
        return(self.id_usuario)
    
    def __init__(self,id_usuario,nombre_usuario,apellido_paterno,apellido_materno,celular_usuario,domicilio_usuario,contrasenia,correo_electronico,rol,estado,creado,editado) -> None:
        self.id_usuario=id_usuario
        self.nombre_usuario=nombre_usuario
        self.apellido_paterno=apellido_paterno
        self.apellido_materno=apellido_materno
        self.celular_usuario=celular_usuario
        self.domicilio_usuario=domicilio_usuario
        self.contrasenia=contrasenia
        self.correo_electronico=correo_electronico
        self.rol=rol
        self.estado=estado
        self.creado=creado 
        self.editado=editado

    @classmethod
    def check_password(self, hashed_password, contrasenia):
        return check_password_hash(hashed_password, contrasenia)
