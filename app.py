import os
from datetime import datetime, timedelta

from flask import (Flask, flash, redirect, render_template, request, send_file,
                   url_for)
from sqlalchemy import inspect, text

from extensions import db
from models import Cliente, Presupuesto
from services.presupuesto_service import (create_presupuesto,
                                          delete_presupuesto,
                                          update_presupuesto)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amoblarte.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_FOLDER'] = os.path.join(os.path.expanduser('~'), 'Desktop', 'Presupuestos')
app.config['LOGO_PATH'] = os.path.join('static', 'logo.png')

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Inicializar DB
db.init_app(app)
with app.app_context():
    db.create_all()
    # Auto-migrate: add new columns if missing (SQLite)
    inspector = inspect(db.engine)
    try:
        cols = {c['name'] for c in inspector.get_columns('presupuestos')}
        alter_stmts = []
        if 'descuento_porcentaje' not in cols:
            alter_stmts.append("ALTER TABLE presupuestos ADD COLUMN descuento_porcentaje FLOAT DEFAULT 0")
        if 'cuotas_3' not in cols:
            alter_stmts.append("ALTER TABLE presupuestos ADD COLUMN cuotas_3 FLOAT DEFAULT 0")
        if 'cuotas_6' not in cols:
            alter_stmts.append("ALTER TABLE presupuestos ADD COLUMN cuotas_6 FLOAT DEFAULT 0")
        if alter_stmts:
            with db.engine.connect() as conn:
                for stmt in alter_stmts:
                    conn.execute(text(stmt))
                conn.commit()
    except Exception:
        pass
    # Auto-cleanup: remove presupuestos older than 2 years (DB + PDF)
    try:
        cutoff = datetime.utcnow() - timedelta(days=730)
        old_items = Presupuesto.query.filter(Presupuesto.fecha_creacion < cutoff).all()
        for p in old_items:
            pdf_filename = f"{p.cliente.nombre_completo}_{p.numero_presupuesto}.pdf"
            pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass
            db.session.delete(p)
        if old_items:
            db.session.commit()
    except Exception:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar')
def buscar():
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

@app.route('/clientes')
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/<int:cliente_id>/presupuestos')
def presupuestos_por_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    presupuestos = Presupuesto.query.filter_by(cliente_id=cliente_id).all()
    return render_template('presupuestos.html', presupuestos=presupuestos, cliente=cliente)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
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

@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
def editar_cliente(id):
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

@app.route('/clientes/<int:id>/eliminar', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente', 'success')
    return redirect(url_for('clientes'))

@app.route('/presupuestos')
def presupuestos():
    presupuestos = Presupuesto.query.join(Cliente).all()
    return render_template('presupuestos.html', presupuestos=presupuestos)

@app.route('/presupuestos/nuevo', methods=['GET', 'POST'])
def nuevo_presupuesto():
    if request.method == 'POST':
        presupuesto = create_presupuesto(request.form, request.files)
        flash('Presupuesto creado exitosamente', 'success')
        return redirect(url_for('presupuestos', pdf_id=presupuesto.id))
    
    clientes = Cliente.query.all()
    return render_template('nuevo_presupuesto.html', clientes=clientes)

@app.route('/presupuestos/<int:id>/editar', methods=['GET', 'POST'])
def editar_presupuesto(id):
    if request.method == 'POST':
        presupuesto = update_presupuesto(id, request.form, request.files)
        flash('Presupuesto actualizado exitosamente', 'success')
        return redirect(url_for('presupuestos', pdf_id=presupuesto.id))
    presupuesto = Presupuesto.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('editar_presupuesto.html', presupuesto=presupuesto, clientes=clientes)

@app.route('/presupuestos/<int:id>/eliminar', methods=['POST'])
def eliminar_presupuesto(id):
    delete_presupuesto(id)
    flash('Presupuesto eliminado exitosamente', 'success')
    return redirect(url_for('presupuestos'))

@app.route('/presupuestos/<int:id>/pdf')
def descargar_pdf(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    pdf_filename = f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf"
    pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=False)
    else:
        flash('PDF no encontrado', 'error')
        return redirect(url_for('presupuestos'))
    # keep module-level exports for tests
from extensions import db as db  # re-export
from models import Cliente as Cliente
from models import Presupuesto as Presupuesto

if __name__ == '__main__':
    app.run(debug=True)
