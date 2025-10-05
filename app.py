#!/usr/bin/env python3
"""Aplicación Flask final funcional"""

import os
import sys
from datetime import datetime, timedelta

from flask import (Flask, flash, redirect, render_template, request, send_file,
                   url_for)
from sqlalchemy import inspect, text

from extensions import db
from models import Cliente, Presupuesto
from services.presupuesto_service import (create_presupuesto,
                                          delete_presupuesto,
                                          update_presupuesto)

# Obtener el directorio base de la aplicación
base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)

app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amoblarte.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'uploads')
app.config['PDF_FOLDER'] = os.path.join(os.path.expanduser('~'), 'Desktop', 'Presupuestos')
app.config['LOGO_PATH'] = os.path.join(base_dir, 'static', 'logo.png')

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Inicializar DB
db.init_app(app)

# Crear tablas de la base de datos
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error en index: {e}")
        return f"Error: {e}", 500

@app.route('/buscar')
def buscar():
    try:
        q = (request.args.get('q') or '').strip()
        clientes = []
        presupuestos = []
        if q:
            like = f"%{q}%"
            clientes = Cliente.query.filter(
                (Cliente.nombre.ilike(like)) | (Cliente.apellido.ilike(like))
            ).all()
            presupuestos = Presupuesto.query.filter(
                Presupuesto.numero_presupuesto.ilike(like)
            ).all()
        return render_template('index.html', q=q, clientes_result=clientes, presupuestos_result=presupuestos)
    except Exception as e:
        print(f"Error en buscar: {e}")
        return f"Error: {e}", 500

@app.route('/clientes')
def clientes():
    try:
        clientes = Cliente.query.all()
        return render_template('clientes.html', clientes=clientes)
    except Exception as e:
        print(f"Error en clientes: {e}")
        return f"Error: {e}", 500

@app.route('/clientes/<int:cliente_id>/presupuestos')
def presupuestos_por_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        presupuestos = Presupuesto.query.filter_by(cliente_id=cliente_id).all()
        return render_template('presupuestos.html', presupuestos=presupuestos, cliente=cliente)
    except Exception as e:
        print(f"Error en presupuestos_por_cliente: {e}")
        return f"Error: {e}", 500

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            celular = request.form['celular']
            direccion = request.form['direccion']
            next_url = request.args.get('next')
            
            cliente = Cliente(
                nombre=nombre,
                apellido=apellido,
                celular=celular,
                direccion=direccion
            )
            
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente creado exitosamente', 'success')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('clientes'))
        
        return render_template('nuevo_cliente.html')
    except Exception as e:
        print(f"Error en nuevo_cliente: {e}")
        return f"Error: {e}", 500

@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        
        if request.method == 'POST':
            cliente.nombre = request.form['nombre']
            cliente.apellido = request.form['apellido']
            cliente.celular = request.form['celular']
            cliente.direccion = request.form['direccion']
            
            db.session.commit()
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('clientes'))
        
        return render_template('editar_cliente.html', cliente=cliente)
    except Exception as e:
        print(f"Error en editar_cliente: {e}")
        return f"Error: {e}", 500

@app.route('/clientes/<int:id>/eliminar', methods=['POST'])
def eliminar_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado exitosamente', 'success')
        return redirect(url_for('clientes'))
    except Exception as e:
        print(f"Error en eliminar_cliente: {e}")
        return f"Error: {e}", 500

@app.route('/presupuestos')
def presupuestos():
    try:
        presupuestos = Presupuesto.query.join(Cliente).all()
        return render_template('presupuestos.html', presupuestos=presupuestos)
    except Exception as e:
        print(f"Error en presupuestos: {e}")
        return f"Error: {e}", 500

@app.route('/presupuestos/nuevo', methods=['GET', 'POST'])
def nuevo_presupuesto():
    try:
        if request.method == 'POST':
            presupuesto = create_presupuesto(request.form, request.files)
            flash('Presupuesto creado exitosamente', 'success')
            return redirect(url_for('presupuestos', pdf_id=presupuesto.id))
        
        clientes = Cliente.query.all()
        return render_template('nuevo_presupuesto.html', clientes=clientes)
    except Exception as e:
        print(f"Error en nuevo_presupuesto: {e}")
        return f"Error: {e}", 500

@app.route('/presupuestos/<int:id>/editar', methods=['GET', 'POST'])
def editar_presupuesto(id):
    try:
        if request.method == 'POST':
            presupuesto = update_presupuesto(id, request.form, request.files)
            flash('Presupuesto actualizado exitosamente', 'success')
            return redirect(url_for('presupuestos', pdf_id=presupuesto.id))
        presupuesto = Presupuesto.query.get_or_404(id)
        clientes = Cliente.query.all()
        return render_template('editar_presupuesto.html', presupuesto=presupuesto, clientes=clientes)
    except Exception as e:
        print(f"Error en editar_presupuesto: {e}")
        return f"Error: {e}", 500

@app.route('/presupuestos/<int:id>/eliminar', methods=['POST'])
def eliminar_presupuesto(id):
    try:
        delete_presupuesto(id)
        flash('Presupuesto eliminado exitosamente', 'success')
        return redirect(url_for('presupuestos'))
    except Exception as e:
        print(f"Error en eliminar_presupuesto: {e}")
        return f"Error: {e}", 500

@app.route('/presupuestos/<int:id>/pdf')
def descargar_pdf(id):
    try:
        presupuesto = Presupuesto.query.get_or_404(id)
        pdf_filename = f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf"
        pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=False)
        else:
            flash('PDF no encontrado', 'error')
            return redirect(url_for('presupuestos'))
    except Exception as e:
        print(f"Error en descargar_pdf: {e}")
        return f"Error: {e}", 500

# keep module-level exports for tests
import threading
import webbrowser

from extensions import db as db  # re-export
from models import Cliente as Cliente
from models import Presupuesto as Presupuesto


def open_browser():
    webbrowser.open("http://127.0.0.1:5001")

if __name__ == "__main__":
    print("=== INICIANDO APLICACIÓN AMOBLARTE ===")
    print(f"Directorio base: {base_dir}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5001)
