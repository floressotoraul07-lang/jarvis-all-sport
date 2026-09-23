from flask import Flask
from models import db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SECRET_KEY'] = 'clave-secreta-cambiala'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'tienda.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)

from views import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos lista")
    app.run(debug=True)
    from flask import make_response
from datetime import datetime as dt

@app.route('/admin/catalogo-pdf')
def catalogo_pdf():
    """Genera el catálogo en PDF para descargar y compartir."""
    sneakers = Sneaker.query.order_by(Sneaker.marca, Sneaker.nombre).all()

    marcas_dict = {}
    for s in sneakers:
        marcas_dict.setdefault(s.marca or 'Otras', []).append(s)

    html = render_template(
        'catalogo_pdf.html',
        marcas=marcas_dict,
        año=dt.now().year,
        whatsapp=WHATSAPP_NUMERO,
        base_path=app.config.get('BASE_DIR', os.getcwd()).replace('\\', '/')
    )

    try:
        from weasyprint import HTML
        pdf = HTML(string=html, base_url=request.url_root).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=catalogo-{dt.now().strftime("%Y%m%d")}.pdf'
        return response
    except ImportError:
        flash('WeasyPrint no está instalado. Ejecuta: pip install weasyprint', 'error')
        return redirect(url_for('admin_dashboard'))