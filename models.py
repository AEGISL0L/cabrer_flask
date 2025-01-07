from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

class RoleEnum(Enum):
    ADMIN = 'admin'
    USUARIO = 'usuario'
    PROFESOR = 'profesor'
    ALUMNO = 'alumno'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(150), unique=True, nullable=False, index=True)
    _password = db.Column('contrasena', db.String(255), nullable=False)
    rol = db.Column(db.Enum(RoleEnum), nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    auditorias = db.relationship('Auditoria', backref='usuario', lazy=True, cascade='all, delete-orphan')
    notificaciones = db.relationship('Notificacion', backref='usuario', lazy=True, cascade='all, delete-orphan')
    productos_asignados = db.relationship('Producto', backref='usuario_asignado_rel', lazy=True,
                                        foreign_keys='Producto.usuario_asignado')
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True, cascade='all, delete-orphan')
    solicitudes = db.relationship('SolicitudPrestamo', backref='solicitante', lazy=True,
                                foreign_keys='SolicitudPrestamo.usuario_id')
    aprobaciones = db.relationship('SolicitudPrestamo', backref='aprobador', lazy=True,
                                 foreign_keys='SolicitudPrestamo.aprobado_por')
    formulas = db.relationship('FormulaPetition', backref='solicitante', lazy=True,
                             foreign_keys='FormulaPetition.usuario_id')

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, plaintext):
        self._password = generate_password_hash(plaintext, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, plaintext):
        return check_password_hash(self._password, plaintext)

class Estado(db.Model):
    __tablename__ = 'estado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7))  # For UI representation
    orden = db.Column(db.Integer)    # For sorting
    
    productos = db.relationship('Producto', backref='estado', lazy=True, cascade='all, delete-orphan')

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    codigo = db.Column(db.String(50), unique=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    usuario_asignado = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id', name='fk_formula_categoria'))
    fecha_asignacion = db.Column(db.DateTime, nullable=True)
    fecha_devolucion = db.Column(db.DateTime, nullable=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultima_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    rfid_tag = db.Column(db.String(100))
    ultimo_escaneo = db.Column(db.DateTime)
    ubicacion_actual = db.Column(db.String(100))
    
    __table_args__ = (
        db.UniqueConstraint('rfid_tag', name='uq_producto_rfid_tag'),
    )
    
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True, cascade='all, delete-orphan')
    escaneos = db.relationship('EscaneoRFID', back_populates='producto', overlaps="historial_ubicaciones")
    historial_ubicaciones = db.relationship('EscaneoRFID', back_populates='producto', order_by='EscaneoRFID.fecha_hora.desc()')
    
class EscaneoRFID(db.Model):
    __tablename__ = 'escaneo_rfid'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ubicacion = db.Column(db.String(100))
    lector_id = db.Column(db.String(100))
    
    producto = db.relationship('Producto', back_populates='escaneos', overlaps="historial_ubicaciones")
    
class Movimiento(db.Model):
    __tablename__ = 'movimiento'
    id = db.Column(db.Integer, primary_key=True)
    formula_id = db.Column(db.Integer, db.ForeignKey('formula_petition.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    estado_anterior = db.Column(db.String(50), nullable=False)
    estado_nuevo = db.Column(db.String(50), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalle = db.Column(db.Text)
    duracion_dias = db.Column(db.Integer)
    razon = db.Column(db.Text)
    fecha_hora_devolucion = db.Column(db.DateTime)

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    formula_id = db.Column(db.Integer, db.ForeignKey('formula_petition.id'))
    accion = db.Column(db.String(150), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalle = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))

class Notificacion(db.Model):
    __tablename__ = 'notificacion'
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(250), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leida = db.Column(db.Boolean, default=False, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    tipo = db.Column(db.String(50))  # For different notification types
    prioridad = db.Column(db.Integer, default=0)
    link = db.Column(db.String(255))  # For notification action URL
    formula_id = db.Column(db.Integer, db.ForeignKey('formula_petition.id'))

class SolicitudPrestamo(db.Model):
    __tablename__ = 'solicitud_prestamo'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)
    razon = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    fecha_aprobacion = db.Column(db.DateTime)
    aprobado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class ConfiguracionSistema(db.Model):
    __tablename__ = 'configuracion_sistema'
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50))
    ultima_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

# Association table for FormulaPetition and Producto
formula_producto = db.Table('formula_producto',
    db.Column('formula_id', db.Integer, db.ForeignKey('formula_petition.id'), primary_key=True),
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id'), primary_key=True),
    db.Column('cantidad', db.Float, nullable=False),
    db.Column('unidad', db.String(10), nullable=False)
)

class FormulaPetition(db.Model):
    __tablename__ = 'formula_petition'
    id = db.Column(db.Integer, primary_key=True)
    petition_id = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    requiere_rele = db.Column(db.String(50))
    telefono_contacto = db.Column(db.String(20), nullable=False)
    foto_receta_path = db.Column(db.String(255))
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')
    fecha_preparacion = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)
    notas_laboratorio = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, nullable=True)

    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    preparado_por_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    
    # Relationships
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref=db.backref('formulas_solicitadas', overlaps="formulas,solicitante"), overlaps="formulas,solicitante")
    preparado_por = db.relationship('Usuario', foreign_keys=[preparado_por_id], backref='formulas_preparadas')
    categoria = db.relationship('Categoria', backref=db.backref('formulas', lazy='dynamic'))
    movimientos = db.relationship('Movimiento', backref='formula', lazy='dynamic')
    notificaciones = db.relationship('Notificacion', backref='formula', lazy='dynamic')
    
    # Add relationship to Producto through association table
    productos = db.relationship('Producto', 
                              secondary=formula_producto,
                              backref=db.backref('formulas', lazy='dynamic'))
    auditorias = db.relationship('Auditoria', backref='formula', lazy='dynamic')

    movimientos = db.relationship('Movimiento', 
                                backref='formula',
                                foreign_keys=[Movimiento.formula_id],
                                lazy='dynamic')                 
    notificaciones = db.relationship('Notificacion', 
                                   backref='formula',
                                   foreign_keys=[Notificacion.formula_id],
                                   lazy='dynamic')
