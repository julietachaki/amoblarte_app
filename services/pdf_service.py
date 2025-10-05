import os
from datetime import datetime

from flask import current_app as app
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)


def generate_pdf(presupuesto):
    # --- Configuración de carpetas y paths ---
    pdf_folder = app.config.get('PDF_FOLDER', 'pdfs')
    os.makedirs(pdf_folder, exist_ok=True)
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    logo_path = app.config.get('LOGO_PATH')

    # --- Nombre y path del PDF ---
    cliente_nombre = getattr(getattr(presupuesto, 'cliente', None), 'nombre_completo', 'SinCliente')
    numero_presupuesto = getattr(presupuesto, 'numero_presupuesto', '0000')
    pdf_filename = f"{cliente_nombre}_{numero_presupuesto}.pdf"
    pdf_path = os.path.join(pdf_folder, pdf_filename)

    # --- Documento ---
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=15, rightMargin=15, topMargin=15, bottomMargin=15)
    story = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize = 12
    bold = ParagraphStyle("bold", parent=normal, fontName="Helvetica-Bold", fontSize=12)

    # --- HEADER ---
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
    else:
        logo = Spacer(1, 2*inch)

    fecha_creacion = getattr(presupuesto, 'fecha_creacion', datetime.now())
    titulo_style = ParagraphStyle("titulo_style", parent=bold, alignment=TA_RIGHT, fontSize=12)
    titulo_fecha = Paragraph(
        f"<b><font size=18 color='#1A237E'>PRESUPUESTO</font></b> "
        f"<br/><font size=10 color='#1A237E'>NRO: {numero_presupuesto}</font>"
        f"<br/><font size=10>Fecha: {fecha_creacion.strftime('%d/%m/%Y')}</font>",
        titulo_style
    )

    header = Table([[logo, titulo_fecha]], colWidths=[1.8*inch, 4.2*inch])
    header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(header)
    story.append(Spacer(1, 40))

    # --- CLIENTE / TELÉFONO ---
    cliente_celular = getattr(getattr(presupuesto, 'cliente', None), 'celular', 'SinTel')
    cliente_tel = Table([
        [Paragraph("<font color='white'><b>CLIENTE</b></font>", bold),
         Paragraph(cliente_nombre, normal),
         Paragraph("<font color='white'><b>TELÉFONO</b></font>", bold),
         Paragraph(cliente_celular, normal)]
    ], colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.3*inch])
    cliente_tel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#07024e")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#07024e")),
        ('TEXTCOLOR', (0,0), (0,0), colors.white),
        ('TEXTCOLOR', (2,0), (2,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(cliente_tel)
    story.append(Spacer(1, 10))

    # --- PROYECTO ---
    descripcion = str(getattr(presupuesto, 'descripcion', '') or "")
    proyecto_tabla = Table([[Paragraph("<font color='white'><b>PROYECTO</b></font>", bold), Paragraph(descripcion, normal)]],
                           colWidths=[1.5*inch, 4.5*inch])
    proyecto_tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#07024e")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(proyecto_tabla)
    story.append(Spacer(1, 60))

    # --- DETALLE ---
    precio_materiales = float(getattr(presupuesto, 'precio_materiales', 0) or 0)
    precio_mano_obra = float(getattr(presupuesto, 'precio_mano_obra', 0) or 0)
    detalle_data = [
        ["ITEM", "DETALLE", "MONTO"],
        ["1", "Materiales: MDF, cantos en PVC, herrajes y accesorios", f"${precio_materiales:,.2f}"],
        ["2", "Mano de obra: fabricación, cortes, colocación", f"${precio_mano_obra:,.2f}"],
    ]
    detalle_table = Table(detalle_data, colWidths=[0.7*inch, 3.8*inch, 1.5*inch])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#07024e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('FONTSIZE', (0,0), (-1,0), 13),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(detalle_table)
    story.append(Spacer(1, 60))

    # --- RESUMEN ---
    total_sin = float(getattr(presupuesto, 'total_sin_tarjeta_con_descuento', 0) or 0)
    total_con = float(getattr(presupuesto, 'total_con_tarjeta', 0) or 0)
    incluye_tarjeta_flag = str(getattr(presupuesto, 'incluye_tarjeta', 'No')).strip().lower() in ["si", "sí", "yes", "y", "true", "1"]

    resumen_rows = [[Paragraph("<b>PRECIO CONTADO/TRANSFERENCIA:</b>", bold), Paragraph(f"${total_sin:,.2f}", normal)]]
    if incluye_tarjeta_flag and total_con > 0:
        resumen_rows.append([Paragraph("<b>PRECIO LISTA:</b>", bold), Paragraph(f"${total_con:,.2f}", normal)])
        for cuotas_attr, label in [('cuotas_3', '3 cuotas de:'), ('cuotas_6', '6 cuotas de:')]:
            cuotas_val = float(getattr(presupuesto, cuotas_attr, 0) or 0)
            if cuotas_val > 0:
                resumen_rows.append([Paragraph(label, bold), f"${cuotas_val:,.2f}"])

    resumen = Table(resumen_rows, colWidths=[4.5*inch, 1.5*inch])
    resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.yellow),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(resumen)
    story.append(Spacer(1, 40))

    # --- NOTAS AL PIE ---
    notas = [
        "Los precios incluyen materiales, mano de obra y traslado.",
        "Garantía de 6 meses por defectos de fabricación.",
        "Atención personalizada y cumplimiento de plazos.",
        "Materiales de primera calidad."
    ]
    nota_style = ParagraphStyle("nota", parent=normal, leftIndent=50, fontSize=12)
    for n in notas:
        story.append(Paragraph(f"✓ {n}", nota_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 40))

    # --- FOOTER ---
    try:
        icon_size = 40
        instagram_path = os.path.join("static", "instagram.png")
        whatsapp_path = os.path.join("static", "whatsapp.png")

        insta_img = Image(instagram_path, width=icon_size, height=icon_size) if os.path.exists(instagram_path) else Spacer(icon_size, icon_size)
        wa_img = Image(whatsapp_path, width=icon_size, height=icon_size) if os.path.exists(whatsapp_path) else Spacer(icon_size, icon_size)

        footer_style = ParagraphStyle("footer_style", parent=bold, fontSize=12, textColor=colors.HexColor("#07024e"), leading=15)
        footer_inner = Table(
            [[insta_img, Paragraph("@_amoblarte", footer_style),
              wa_img, Paragraph("2604454455", footer_style)]],
            colWidths=[0.25*inch, 2.2*inch, 0.25*inch, 2.2*inch]
        )
        footer_inner.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ]))
        full_footer = Table([[footer_inner]], colWidths=[6*inch])
        full_footer.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('LEFTPADDING', (0,0), (-1,-1), 30),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(full_footer)
    except Exception:
        pass

    # --- IMAGEN PRINCIPAL ---
    try:
        if getattr(presupuesto, 'imagen', None):
            image_path = os.path.join(upload_folder, presupuesto.imagen)
            if os.path.exists(image_path):
                story.append(PageBreak())
                with PILImage.open(image_path) as pil_img:
                    img_w, img_h = pil_img.size
                page_width, page_height = letter
                max_w = page_width - (doc.leftMargin + doc.rightMargin)
                max_h = page_height - (doc.topMargin + doc.bottomMargin)
                scale = min(max_w / img_w, max_h / img_h)
                rl_img = Image(image_path, width=img_w*scale, height=img_h*scale)
                rl_img.hAlign = 'CENTER'
                story.append(Spacer(1, 12))
                story.append(rl_img)
    except Exception:
        pass

    # --- GENERAR PDF ---
    doc.build(story)
    return pdf_path
