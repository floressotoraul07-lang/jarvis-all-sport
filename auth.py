from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Aquí defines TU usuario y contraseña
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def check_password(self, password_input):
        # Verifica si la contraseña ingresada es correcta
        return check_password_hash(self.password, password_input)

# Creamos el usuario dueño (Tú)
# Usuario: jarvis_admin | Contraseña: Jarvis2026!
USERS = {
    'jarvis_admin': User(1, 'jarvis_admin', generate_password_hash('60087654*'))
}

def get_user(username):
    return USERS.get(username)