import os
import uuid
from datetime import datetime

from flask import current_app as app
from werkzeug.utils import secure_filename

from extensions import db
from models import Cliente, Presupuesto
from services.pdf_service import generate_pdf


def _next_serial_number() -> str:
    # Get all existing numbers and compute next integer serial (numeric only)
    existing = db.session.query(Presupuesto.numero_presupuesto).all()
    max_num = 0
    for (num_str,) in existing:
        try:
            # accept numbers possibly stored as strings with spaces
            n = int(str(num_str).strip())
            if n > max_num:
                max_num = n
        except (ValueError, TypeError):
            continue
    return str(max_num + 1)


def create_presupuesto(form, files):
    cliente_id = form.get('cliente_id')
    descripcion = form.get('descripcion')
    precio_materiales = float(form.get('precio_materiales') or 0)
    precio_mano_obra = float(form.get('precio_mano_obra') or 0)
    incluye_tarjeta = form.get('incluye_tarjeta', 'No')
    precio_tarjeta = float(form.get('precio_tarjeta') or 0)
    descuento_porcentaje = float(form.get('descuento_porcentaje') or 0)
    cuotas_3 = float(form.get('cuotas_3') or 0)
    cuotas_6 = float(form.get('cuotas_6') or 0)

    numero_presupuesto = _next_serial_number()

    imagen = None
    if 'imagen' in files:
        file = files['imagen']
        if file and file.filename:
            filename = secure_filename(file.filename)
            filename = f"{numero_presupuesto}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen = filename

    presupuesto = Presupuesto(
        numero_presupuesto=numero_presupuesto,
        descripcion=descripcion,
        imagen=imagen,
        precio_materiales=precio_materiales,
        precio_mano_obra=precio_mano_obra,
        precio_tarjeta=precio_tarjeta,
        incluye_tarjeta=incluye_tarjeta,
        descuento_porcentaje=descuento_porcentaje,
        cuotas_3=cuotas_3,
        cuotas_6=cuotas_6,
        cliente_id=cliente_id
    )
    db.session.add(presupuesto)
    db.session.commit()

    generate_pdf(presupuesto)
    return presupuesto


def update_presupuesto(presupuesto_id, form, files):
    presupuesto = Presupuesto.query.get_or_404(presupuesto_id)

    presupuesto.descripcion = form.get('descripcion')
    presupuesto.precio_materiales = float(form.get('precio_materiales') or 0)
    presupuesto.precio_mano_obra = float(form.get('precio_mano_obra') or 0)
    presupuesto.incluye_tarjeta = form.get('incluye_tarjeta', 'No')
    presupuesto.precio_tarjeta = float(form.get('precio_tarjeta') or 0)
    presupuesto.descuento_porcentaje = float(form.get('descuento_porcentaje') or presupuesto.descuento_porcentaje or 0)
    presupuesto.cuotas_3 = float(form.get('cuotas_3') or presupuesto.cuotas_3 or 0)
    presupuesto.cuotas_6 = float(form.get('cuotas_6') or presupuesto.cuotas_6 or 0)

    if 'imagen' in files:
        file = files['imagen']
        if file and file.filename:
            if presupuesto.imagen:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], presupuesto.imagen)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            filename = f"{presupuesto.numero_presupuesto}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            presupuesto.imagen = filename

    db.session.commit()

    generate_pdf(presupuesto)
    return presupuesto


def delete_presupuesto(presupuesto_id):
    presupuesto = Presupuesto.query.get_or_404(presupuesto_id)

    if presupuesto.imagen:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], presupuesto.imagen)
        if os.path.exists(image_path):
            os.remove(image_path)

    pdf_path = os.path.join(app.config['PDF_FOLDER'], f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    db.session.delete(presupuesto)
    db.session.commit()

    return True
