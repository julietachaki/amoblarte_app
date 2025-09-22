import io
import os
import uuid
from datetime import datetime

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, url_for)
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amoblarte.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_FOLDER'] = os.path.join(os.path.expanduser('~'), 'Desktop', 'Presupuestos')

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Definir modelos aquí para que hereden de db.Model
class Cliente(db.Model):
    __tablename__ = "clientes"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con presupuestos
    presupuestos = db.relationship("Presupuesto", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente {self.nombre} {self.apellido}>"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Presupuesto(db.Model):
    __tablename__ = "presupuestos"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    numero_presupuesto = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))  # Ruta de la imagen
    precio_materiales = db.Column(db.Float, default=0.0)
    precio_mano_obra = db.Column(db.Float, default=0.0)
    precio_tarjeta = db.Column(db.Float, default=0.0)
    incluye_tarjeta = db.Column(db.String(10), default="No")  # "Sí" o "No"
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Clave foránea
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    
    # Relación con cliente
    cliente = db.relationship("Cliente", back_populates="presupuestos")
    
    def __repr__(self):
        return f"<Presupuesto {self.numero_presupuesto}>"
    
    @property
    def total_sin_tarjeta(self):
        return self.precio_materiales + self.precio_mano_obra
    
    @property
    def total_con_tarjeta(self):
        return self.total_sin_tarjeta + self.precio_tarjeta
    
    @property
    def total_final(self):
        if self.incluye_tarjeta == "Sí":
            return self.total_con_tarjeta
        return self.total_sin_tarjeta

# Crear tablas
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        celular = request.form['celular']
        direccion = request.form['direccion']
        
        cliente = Cliente(
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            direccion=direccion
        )
        
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado exitosamente', 'success')
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
        # Obtener datos del formulario
        cliente_id = request.form.get('cliente_id')
        descripcion = request.form['descripcion']
        precio_materiales = float(request.form['precio_materiales'])
        precio_mano_obra = float(request.form['precio_mano_obra'])
        incluye_tarjeta = request.form.get('incluye_tarjeta', 'No')
        precio_tarjeta = float(request.form.get('precio_tarjeta', 0))
        
        # Generar número de presupuesto único
        numero_presupuesto = f"PRE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        # Manejar imagen
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = f"{numero_presupuesto}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen = filename
        
        # Crear presupuesto
        presupuesto = Presupuesto(
            numero_presupuesto=numero_presupuesto,
            descripcion=descripcion,
            imagen=imagen,
            precio_materiales=precio_materiales,
            precio_mano_obra=precio_mano_obra,
            precio_tarjeta=precio_tarjeta,
            incluye_tarjeta=incluye_tarjeta,
            cliente_id=cliente_id
        )
        
        db.session.add(presupuesto)
        db.session.commit()
        
        # Generar PDF
        generar_pdf(presupuesto.id)
        
        flash('Presupuesto creado exitosamente', 'success')
        return redirect(url_for('presupuestos'))
    
    clientes = Cliente.query.all()
    return render_template('nuevo_presupuesto.html', clientes=clientes)

@app.route('/presupuestos/<int:id>/editar', methods=['GET', 'POST'])
def editar_presupuesto(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    
    if request.method == 'POST':
        presupuesto.descripcion = request.form['descripcion']
        presupuesto.precio_materiales = float(request.form['precio_materiales'])
        presupuesto.precio_mano_obra = float(request.form['precio_mano_obra'])
        presupuesto.incluye_tarjeta = request.form.get('incluye_tarjeta', 'No')
        presupuesto.precio_tarjeta = float(request.form.get('precio_tarjeta', 0))
        
        # Manejar nueva imagen
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename:
                # Eliminar imagen anterior si existe
                if presupuesto.imagen:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], presupuesto.imagen)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filename = f"{presupuesto.numero_presupuesto}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                presupuesto.imagen = filename
        
        db.session.commit()
        
        # Regenerar PDF
        generar_pdf(presupuesto.id)
        
        flash('Presupuesto actualizado exitosamente', 'success')
        return redirect(url_for('presupuestos'))
    
    clientes = Cliente.query.all()
    return render_template('editar_presupuesto.html', presupuesto=presupuesto, clientes=clientes)

@app.route('/presupuestos/<int:id>/eliminar', methods=['POST'])
def eliminar_presupuesto(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    
    # Eliminar imagen si existe
    if presupuesto.imagen:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], presupuesto.imagen)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Eliminar PDF si existe
    pdf_path = os.path.join(app.config['PDF_FOLDER'], f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    db.session.delete(presupuesto)
    db.session.commit()
    flash('Presupuesto eliminado exitosamente', 'success')
    return redirect(url_for('presupuestos'))

@app.route('/presupuestos/<int:id>/pdf')
def descargar_pdf(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    pdf_filename = f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf"
    pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        flash('PDF no encontrado', 'error')
        return redirect(url_for('presupuestos'))

def generar_pdf(presupuesto_id):
    presupuesto = Presupuesto.query.get(presupuesto_id)
    if not presupuesto:
        return
    
    # Crear nombre del archivo
    pdf_filename = f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf"
    pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
    
    # Crear documento PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    story.append(Paragraph("PRESUPUESTO", title_style))
    story.append(Spacer(1, 20))
    
    # Información del presupuesto
    info_data = [
        ['Número de Presupuesto:', presupuesto.numero_presupuesto],
        ['Fecha:', presupuesto.fecha_creacion.strftime('%d/%m/%Y')],
        ['Cliente:', presupuesto.cliente.nombre_completo],
        ['Celular:', presupuesto.cliente.celular],
        ['Dirección:', presupuesto.cliente.direccion]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Descripción
    if presupuesto.descripcion:
        story.append(Paragraph("Descripción:", styles['Heading2']))
        story.append(Paragraph(presupuesto.descripcion, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Tabla de precios
    precio_data = [
        ['Concepto', 'Precio ($)'],
        ['Materiales', f"${presupuesto.precio_materiales:,.2f}"],
        ['Mano de Obra', f"${presupuesto.precio_mano_obra:,.2f}"],
        ['Subtotal', f"${presupuesto.total_sin_tarjeta:,.2f}"]
    ]
    
    if presupuesto.incluye_tarjeta == "Sí":
        precio_data.append(['Precio con Tarjeta', f"${presupuesto.precio_tarjeta:,.2f}"])
        precio_data.append(['TOTAL', f"${presupuesto.total_con_tarjeta:,.2f}"])
    else:
        precio_data.append(['TOTAL', f"${presupuesto.total_sin_tarjeta:,.2f}"])
    
    precio_table = Table(precio_data, colWidths=[3*inch, 2*inch])
    precio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(precio_table)
    
    # Construir PDF
    doc.build(story)

if __name__ == '__main__':
    app.run(debug=True)
