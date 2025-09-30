import os

from flask import current_app as app
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


def generate_pdf(presupuesto):
    pdf_filename = f"{presupuesto.cliente.nombre_completo}_{presupuesto.numero_presupuesto}.pdf"
    pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize= letter , leftMargin=15, rightMargin=15, topMargin=15,bottomMargin = 15)
    story = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize=12
    bold = ParagraphStyle("bold", parent=normal, fontName="Helvetica-Bold",fontSize=12)

    # --- HEADER ---
    logo_path = app.config.get("LOGO_PATH")
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
    else:
        logo = Spacer(1, 2*inch)
    
    titulo_style = ParagraphStyle(
        "titulo_style",
        parent=bold,
        alignment= TA_RIGHT, 
        fontSize=12
    )
    titulo_fecha = Paragraph(
        f"<b><font size=18 color='#1A237E'>PRESUPUESTO</font></b> "
        f"<br/><font size=10 color='#1A237E'>NRO: {presupuesto.numero_presupuesto}</font>"
        f"<br/><font size=10>Fecha: {presupuesto.fecha_creacion.strftime('%d/%m/%Y')}</font>",
        titulo_style
    )

    header = Table([[logo, titulo_fecha]], colWidths=[1.8*inch, 4.2*inch])
    header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header)
    story.append(Spacer(1, 40))

    # --- CLIENTE / TELÉFONO ---
    cliente_tel = Table([
        [Paragraph("<font color='white'><b>CLIENTE</b></font>",bold),Paragraph( presupuesto.cliente.nombre_completo,normal),
         Paragraph("<font color='white'><b>TELÉFONO</b></font>", bold), Paragraph(presupuesto.cliente.celular,normal)]
    ], colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.3*inch])
    cliente_tel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#07024e")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#07024e")),
        ('TEXTCOLOR', (0,0), (0,0), colors.white),                 # texto CLIENTE
        ('TEXTCOLOR', (2,0), (2,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(cliente_tel)
    story.append(Spacer(1, 10))

    # --- PROYECTO ---
    proyecto_tabla = Table([
        [Paragraph("<font color='white'><b>PROYECTO</b></font>", bold), Paragraph(presupuesto.descripcion or "",normal)]
    ], colWidths=[1.5*inch, 4.5*inch])
    proyecto_tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#07024e")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(proyecto_tabla)
    story.append(Spacer(1, 60))

    # --- DETALLE ---
    detalle_data = [
        ["ITEM", "DETALLE", "MONTO"],
        ["1", "Materiales: MDF,cantos en PVC,herrajes y accesorios", f"${presupuesto.precio_materiales:,.2f}"],
        ["2", "Mano de obra: fabricación, cortes, colocación", f"${presupuesto.precio_mano_obra:,.2f}"],
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
    total_sin = f"${presupuesto.total_sin_tarjeta_con_descuento:,.2f}"
    resumen_rows = [[Paragraph("<b>PRECIO CONTADO/TRANSFERENCIA:</b>", bold),Paragraph( total_sin,normal)]]

    incluye_tarjeta_flag = (presupuesto.incluye_tarjeta or "No").strip().lower() in ["si", "sí", "yes", "y", "true", "1"]
    if incluye_tarjeta_flag and (presupuesto.precio_tarjeta or 0) > 0:
        total_con = f"${presupuesto.total_con_tarjeta:,.2f}"
        resumen_rows.append([Paragraph("<b>PRECIO LISTA:</b>", bold),Paragraph( total_con,normal)])
        if (presupuesto.cuotas_3 or 0) > 0:
            resumen_rows.append([Paragraph("3 cuotas de:", bold), f"${presupuesto.cuotas_3:,.2f}"])
        if (presupuesto.cuotas_6 or 0) > 0:
            resumen_rows.append([Paragraph("6 cuotas de:", bold), f"${presupuesto.cuotas_6:,.2f}"])

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

    nota_style = ParagraphStyle(
        "nota",
        parent=normal,
        leftIndent=50,   # margen izquierdo uniforme
        fontSize=12,
    )

    for n in notas:
        story.append(Paragraph(f"✓ {n}", nota_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 40))

    # --- FOOTER (franja completa con Instagram + usuario y WhatsApp a la derecha) ---
    icon_size = 40  # tamaño de los íconos en puntos

    instagram_path = os.path.join("static", "instagram.png")
    whatsapp_path = os.path.join("static", "whatsapp.png")

    # Si no existe la imagen, mostramos un spacer (deja el texto visible)
    insta_img = Image(instagram_path, width=icon_size, height=icon_size) if os.path.exists(instagram_path) else Spacer(icon_size, icon_size)
    wa_img = Image(whatsapp_path, width=icon_size, height=icon_size) if os.path.exists(whatsapp_path) else Spacer(icon_size, icon_size)

    # Estilo del texto del footer (blanco)
    footer_style = ParagraphStyle(
        "footer_style",
        parent=bold,
        fontSize=12,
        textColor=colors.HexColor("#07024e"),
        leading=15
    )

    # Tabla interna con: [icono insta, usuario, icono wa, número]
    footer_inner = Table(
        [[insta_img, Paragraph("@_amoblarte", footer_style),
          wa_img, Paragraph("2604454455", footer_style)]],
        colWidths=[0.25*inch, 2.2*inch, 0.25*inch, 2.2*inch]
    )
    footer_inner.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),    # todo alineado a la derecha dentro de la franja
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        # También podemos asegurar que el texto interno esté blanco (por si no usás footer_style)
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
    ]))

    # Contenedor full-width con fondo (franja)
    full_footer = Table([[footer_inner]], colWidths=[6*inch])
    full_footer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),  # color de la franja
        ('LEFTPADDING', (0,0), (-1,-1), 30),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    # Añadir al story
    story.append(full_footer)


    doc.build(story)

    return pdf_path
