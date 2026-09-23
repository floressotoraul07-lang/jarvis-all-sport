from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Sneaker(db.Model):
    __tablename__ = 'sneaker'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=True)          # Ej: 750SMA0077APE
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50), nullable=False)           # Nike, Adidas, Puma...
    genero = db.Column(db.String(20), default='Caballero')     # Caballero, Dama, Niño
    categoria = db.Column(db.String(20), default='Adulto')     # Adulto, Niño
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    precio_oferta = db.Column(db.Float, nullable=True)         # Precio tachado (opcional)
    imagen_url = db.Column(db.String(200), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    inventarios = db.relationship('Inventory', backref='sneaker', lazy=True, cascade="all, delete-orphan")


class Size(db.Model):
    __tablename__ = 'size'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)  # "39.5", "40", "41"
    inventarios = db.relationship('Inventory', backref='size', lazy=True, cascade="all, delete-orphan")


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    sneaker_id = db.Column(db.Integer, db.ForeignKey('sneaker.id'), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('sneaker_id', 'size_id', name='unique_inventory'),)