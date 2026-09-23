from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import uuid
from urllib.parse import quote

from app import app, db
from models import Sneaker, Size, Inventory

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ⚙️ CONFIGURACIÓN DE LA TIENDA
NOMBRE_TIENDA = "JARVIS ALL SPORT"
WHATSAPP_NUMERO = "51925339422"
WHATSAPP_NUMERO_2 = "51956877923"
MARCAS = ["Nike", "Adidas", "Puma", "Lacoste", "Jordan", "Fila", "Reebok", "New Balance"]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def guardar_imagen(imagen):
    if imagen and imagen.filename and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        filename = f"{uuid.uuid4().hex}_{filename}"
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagen.save(ruta)
        return f"uploads/{filename}"
    return None


def borrar_imagen(imagen_url):
    if not imagen_url:
        return
    try:
        nombre = imagen_url.split('/')[-1]
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre)
        if os.path.exists(ruta):
            os.remove(ruta)
    except Exception:
        pass


# ============================================================
# BIENVENIDA
# ============================================================
@app.route('/')
def bienvenida():
    return render_template('bienvenida.html', nombre_tienda=NOMBRE_TIENDA)


# ============================================================
# CATÁLOGO PÚBLICO
# ============================================================
@app.route('/catalogo')
def catalogo():
    marca_filtro = request.args.get('marca', '')
    categoria_filtro = request.args.get('categoria', '')

    query = Sneaker.query
    if marca_filtro:
        query = query.filter(Sneaker.marca == marca_filtro)
    if categoria_filtro:
        query = query.filter(Sneaker.categoria == categoria_filtro)

    sneakers = query.order_by(Sneaker.fecha_creacion.desc()).all()

    return render_template(
        'catalogo.html',
        sneakers=sneakers,
        marcas=MARCAS,
        marca_activa=marca_filtro,
        categoria_activa=categoria_filtro,
        nombre_tienda=NOMBRE_TIENDA,
        whatsapp=WHATSAPP_NUMERO
    )


@app.route('/detalle/<int:sneaker_id>')
def detalle(sneaker_id):
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    inventarios = Inventory.query.join(Size).filter(
        Inventory.sneaker_id == sneaker_id
    ).order_by(Size.numero).all()

    mensaje = f"Hola {NOMBRE_TIENDA}, me interesa la zapatilla {sneaker.marca} {sneaker.nombre}"
    if sneaker.codigo:
        mensaje += f" (Cód. {sneaker.codigo})"
    mensaje += f". ¿Está disponible?"
    mensaje_url = quote(mensaje)

    return render_template(
        'detalle.html',
        sneaker=sneaker,
        inventarios=inventarios,
        nombre_tienda=NOMBRE_TIENDA,
        whatsapp=WHATSAPP_NUMERO,
        mensaje_url=mensaje_url
    )


# ============================================================
# ADMIN
# ============================================================
@app.route('/admin')
def admin_dashboard():
    marca_filtro = request.args.get('marca', '')
    query = Sneaker.query
    if marca_filtro:
        query = query.filter(Sneaker.marca == marca_filtro)
    sneakers = query.order_by(Sneaker.fecha_creacion.desc()).all()
    return render_template('admin_dashboard.html', sneakers=sneakers, marcas=MARCAS, marca_activa=marca_filtro)


@app.route('/admin/agregar', methods=['GET', 'POST'])
def agregar_sneaker():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        marca = request.form.get('marca', '').strip()
        genero = request.form.get('genero', 'Caballero')
        categoria = request.form.get('categoria', 'Adulto')
        codigo = request.form.get('codigo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        try:
            precio = float(request.form.get('precio', 0))
        except ValueError:
            flash('Precio inválido', 'error')
            return redirect(url_for('agregar_sneaker'))

        precio_oferta_str = request.form.get('precio_oferta', '').strip()
        precio_oferta = float(precio_oferta_str) if precio_oferta_str else None

        imagen_url = guardar_imagen(request.files.get('imagen'))

        nueva = Sneaker(
            nombre=nombre, marca=marca, genero=genero, categoria=categoria,
            codigo=codigo, descripcion=descripcion, precio=precio,
            precio_oferta=precio_oferta, imagen_url=imagen_url
        )
        db.session.add(nueva)
        db.session.flush()

        tallas = request.form.getlist('talla[]')
        cantidades = request.form.getlist('cantidad[]')
        for t, c in zip(tallas, cantidades):
            t = t.strip()
            if not t or not c:
                continue
            try:
                cant = int(c)
            except ValueError:
                continue
            size = Size.query.filter_by(numero=t).first()
            if not size:
                size = Size(numero=t)
                db.session.add(size)
                db.session.flush()
            db.session.add(Inventory(sneaker_id=nueva.id, size_id=size.id, cantidad=cant))

        db.session.commit()
        flash('Zapatilla agregada', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_form.html', sneaker=None, inventarios=[], marcas=MARCAS)


@app.route('/admin/editar/<int:sneaker_id>', methods=['GET', 'POST'])
def editar_sneaker(sneaker_id):
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    if request.method == 'POST':
        sneaker.nombre = request.form.get('nombre', '').strip()
        sneaker.marca = request.form.get('marca', '').strip()
        sneaker.genero = request.form.get('genero', 'Caballero')
        sneaker.categoria = request.form.get('categoria', 'Adulto')
        sneaker.codigo = request.form.get('codigo', '').strip()
        sneaker.descripcion = request.form.get('descripcion', '').strip()
        try:
            sneaker.precio = float(request.form.get('precio', 0))
        except ValueError:
            flash('Precio inválido', 'error')
            return redirect(url_for('editar_sneaker', sneaker_id=sneaker.id))

        precio_oferta_str = request.form.get('precio_oferta', '').strip()
        sneaker.precio_oferta = float(precio_oferta_str) if precio_oferta_str else None

        imagen = request.files.get('imagen')
        if imagen and imagen.filename:
            nueva_url = guardar_imagen(imagen)
            if nueva_url:
                borrar_imagen(sneaker.imagen_url)
                sneaker.imagen_url = nueva_url

        Inventory.query.filter_by(sneaker_id=sneaker.id).delete()
        tallas = request.form.getlist('talla[]')
        cantidades = request.form.getlist('cantidad[]')
        for t, c in zip(tallas, cantidades):
            t = t.strip()
            if not t or not c:
                continue
            try:
                cant = int(c)
            except ValueError:
                continue
            size = Size.query.filter_by(numero=t).first()
            if not size:
                size = Size(numero=t)
                db.session.add(size)
                db.session.flush()
            db.session.add(Inventory(sneaker_id=sneaker.id, size_id=size.id, cantidad=cant))

        db.session.commit()
        flash('Zapatilla actualizada', 'success')
        return redirect(url_for('admin_dashboard'))

    inventarios = Inventory.query.join(Size).filter(
        Inventory.sneaker_id == sneaker.id
    ).order_by(Size.numero).all()
    return render_template('admin_form.html', sneaker=sneaker, inventarios=inventarios, marcas=MARCAS)


@app.route('/admin/eliminar/<int:sneaker_id>', methods=['POST'])
def eliminar_sneaker(sneaker_id):
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    borrar_imagen(sneaker.imagen_url)
    db.session.delete(sneaker)
    db.session.commit()
    flash('Zapatilla eliminada', 'warning')
    return redirect(url_for('admin_dashboard'))
@app.route('/compartir-catalogo')
def compartir_catalogo():
    """Genera un mensaje con TODOS los productos para enviar por WhatsApp."""
    sneakers = Sneaker.query.order_by(Sneaker.marca, Sneaker.nombre).all()

    lineas = [f"*CATÁLOGO {NOMBRE_TIENDA}*\n"]
    marca_actual = None

    for s in sneakers:
        if s.marca != marca_actual:
            marca_actual = s.marca
            lineas.append(f"\n*=== {marca_actual.upper()} ===*")

        linea = f"\n👟 *{s.nombre}*"
        if s.codigo:
            linea += f"\n   Cód: {s.codigo}"
        linea += f"\n   Precio: S/ {s.precio:.2f}"

        tallas = [inv.size.numero for inv in s.inventarios]
        if tallas:
            linea += f"\n   Tallas: {', '.join(tallas)}"

        lineas.append(linea)

    lineas.append(f"\n\n📞 Pide el tuyo al WhatsApp: +{WHATSAPP_NUMERO}")

    mensaje = "\n".join(lineas)
    mensaje_url = quote(mensaje)

    return redirect(f"https://wa.me/?text={mensaje_url}")