from flask import Flask
from models import db
import os

# Importamos la herramienta de seguridad
from flask_login import LoginManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SECRET_KEY'] = 'clave-super-secreta-cambiala-por-favor'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'tienda.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)

# ============================================================
# CONFIGURACIÓN DE SEGURIDAD (LOGIN)
# ============================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si alguien intenta entrar al admin sin permiso, lo manda aquí
login_manager.login_message = 'Debes iniciar sesión para entrar al panel.'

from auth import get_user

@login_manager.user_loader
def load_user(user_id):
    # Busca al usuario en auth.py
    for user in get_user.__globals__['USERS'].values():
        if str(user.id) == str(user_id):
            return user
    return None
# ============================================================

from views import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos lista")
    app.run(debug=True)

