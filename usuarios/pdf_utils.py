from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Drawing, Line, Rect
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

def generar_comprobante_venta(venta_data, detalles):
    buffer = BytesIO()
    
    # --- Configuración del Documento ---
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=40,
        bottomMargin=40
    )
    
    elements = []
    styles = getSampleStyleSheet()

    # --- COLORES PROFESIONALES ---
    negro = colors.HexColor('#000000')
    gris_oscuro = colors.HexColor('#333333')
    gris_medio = colors.HexColor('#666666')
    gris_claro = colors.HexColor('#aaaaaa')
    gris_muy_claro = colors.HexColor('#f5f5f5')

    # --- ESTILOS LIMPIOS ---
    style_slogan = ParagraphStyle(
        'Slogan', 
        parent=styles['Normal'], 
        fontName='Helvetica-Oblique', 
        fontSize=9, 
        textColor=gris_medio, 
        alignment=TA_LEFT, 
        spaceAfter=6
    )
    
    style_address = ParagraphStyle(
        'Address', 
        parent=styles['Normal'], 
        fontName='Helvetica', 
        fontSize=8.5, 
        leading=11, 
        textColor=gris_medio, 
        alignment=TA_LEFT
    )
    
    style_comprobante = ParagraphStyle(
        'Comprobante', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=18, 
        leading=22, 
        alignment=TA_RIGHT, 
        textColor=negro,
        spaceAfter=4
    )
    
    style_numero = ParagraphStyle(
        'Numero', 
        parent=styles['Normal'], 
        fontName='Helvetica', 
        fontSize=11, 
        alignment=TA_RIGHT, 
        textColor=gris_oscuro
    )
    
    style_label = ParagraphStyle(
        'Label', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold',
        fontSize=9, 
        textColor=gris_oscuro
    )
    
    style_value = ParagraphStyle(
        'Value', 
        parent=styles['Normal'], 
        fontName='Helvetica',
        fontSize=9.5, 
        textColor=negro
    )
    
    style_item = ParagraphStyle(
        'Item', 
        parent=styles['Normal'], 
        fontSize=9.5, 
        leading=13, 
        textColor=negro
    )

    # --- 1. ENCABEZADO ---
    
    logo_path = os.path.join(settings.BASE_DIR, 'logo_barberia.jpg')
    
    logo_img = None
    if os.path.exists(logo_path):
        try:
            logo_img = Image(logo_path, width=3.8*cm, height=3.8*cm) 
            logo_img.hAlign = 'LEFT'
        except Exception as e:
            print(f"Error cargando imagen logo: {e}")
    else:
        print(f"⚠️ No se encontró el logo en: {logo_path}")

    direccion_texto = """
    Avenida Libertador 600<br/>
    Galería Rosa - Local 3<br/>
    Tel: (3755) 12-3456<br/>
    contacto@hairsoft.com
    """
    
    info_izq = []
    if logo_img:
        info_izq.append(logo_img)
        info_izq.append(Spacer(1, 8))
    
    info_izq.append(Paragraph('"Los Últimos Serán Los Primeros"', style_slogan))
    info_izq.append(Paragraph(direccion_texto, style_address))

    # Info derecha - comprobante
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    fecha_venta = venta_data.get('fecha')
    
    if fecha_venta:
        try:
            if 'T' in str(fecha_venta):
                dt = datetime.fromisoformat(str(fecha_venta).replace('Z', '+00:00'))
                fecha_texto = dt.strftime("%d/%m/%Y %H:%M")
            else:
                fecha_texto = str(fecha_venta)
        except:
            fecha_texto = fecha_actual
    else:
        fecha_texto = fecha_actual

    info_der = [
        Paragraph("COMPROBANTE DE VENTA", style_comprobante),
        Paragraph(f"N° {venta_data.get('id', '000'):0>6}", style_numero),
        Spacer(1, 8),
        Paragraph(f"Fecha: {fecha_texto}", ParagraphStyle('Fecha', parent=style_numero, fontSize=9)),
        Spacer(1, 12),
        Paragraph("DOCUMENTO NO FISCAL", ParagraphStyle('NoFiscal', parent=style_numero, fontSize=7, textColor=gris_claro)),
    ]

    header_table = Table([[info_izq, info_der]], colWidths=[9.5*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # Línea separadora gruesa
    d = Drawing(495, 2)
    d.add(Rect(0, 0, 495, 2, fillColor=negro, strokeColor=None))
    elements.append(d)
    elements.append(Spacer(1, 0.8*cm))

    # --- 2. INFORMACIÓN DE LA VENTA ---
    
    cliente_nombre = venta_data.get('cliente_nombre') or "Consumidor Final"
    usuario_vendedor = venta_data.get('usuario_nombre') or "Sistema"
    medio_pago = venta_data.get('medio_pago_nombre') or 'Efectivo'

    info_venta = [
        [Paragraph("CLIENTE", style_label), Paragraph(cliente_nombre, style_value)],
        [Paragraph("ATENDIDO POR", style_label), Paragraph(usuario_vendedor, style_value)],
        [Paragraph("FORMA DE PAGO", style_label), Paragraph(medio_pago, style_value)],
    ]

    tabla_info = Table(info_venta, colWidths=[4*cm, 13.5*cm])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), gris_muy_claro),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    elements.append(tabla_info)
    elements.append(Spacer(1, 1*cm))

    # --- 3. DETALLE DE ITEMS ---
    
    style_header = ParagraphStyle('Header', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
    
    headers = [
        Paragraph('DESCRIPCIÓN', style_header),
        Paragraph('CANT.', ParagraphStyle('HC', parent=style_header, alignment=TA_CENTER)),
        Paragraph('P. UNITARIO', ParagraphStyle('HR', parent=style_header, alignment=TA_RIGHT)),
        Paragraph('TOTAL', ParagraphStyle('HR', parent=style_header, alignment=TA_RIGHT)),
    ]
    data_items = [headers]
    
    for detalle in detalles:
        nombre = "Item"
        if hasattr(detalle, 'producto') and detalle.producto:
            nombre = detalle.producto.nombre
        elif hasattr(detalle, 'servicio') and detalle.servicio:
            nombre = detalle.servicio.nombre
        elif hasattr(detalle, 'turno') and detalle.turno:
            nombre = f"Turno #{detalle.turno.id}"
        
        precio_fmt = f"${detalle.precio_unitario:,.2f}"
        subtotal_fmt = f"${detalle.subtotal:,.2f}"

        row = [
            Paragraph(nombre, style_item),
            Paragraph(str(int(detalle.cantidad)), ParagraphStyle('IC', parent=style_item, alignment=TA_CENTER)),
            Paragraph(precio_fmt, ParagraphStyle('IR', parent=style_item, alignment=TA_RIGHT)),
            Paragraph(subtotal_fmt, ParagraphStyle('IR', parent=style_item, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
        ]
        data_items.append(row)

    tabla_items = Table(data_items, colWidths=[8.5*cm, 2.5*cm, 3.25*cm, 3.25*cm])
    
    tabla_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), negro),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,1), (-1,-1), 11),
        ('BOTTOMPADDING', (0,1), (-1,-1), 11),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, gris_claro),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(tabla_items)
    elements.append(Spacer(1, 0.8*cm))

    # --- 4. TOTAL ---
    total_final = float(venta_data.get('total', 0))
    
    style_total = ParagraphStyle('Total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=TA_RIGHT, textColor=negro)

    tabla_total = Table([
        [Paragraph("TOTAL", ParagraphStyle('TL', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_RIGHT)), 
         Paragraph(f"${total_final:,.2f}", style_total)]
    ], colWidths=[13.5*cm, 4*cm])
    
    tabla_total.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 2.5, negro),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('BACKGROUND', (1,0), (1,0), gris_muy_claro),
        ('RIGHTPADDING', (1,0), (1,0), 10),
    ]))
    
    elements.append(tabla_total)
    elements.append(Spacer(1, 3*cm))

    # --- 5. FOOTER MINIMALISTA ---
    
    d_line = Drawing(495, 1)
    d_line.add(Line(0, 0, 495, 0, strokeColor=gris_claro, strokeWidth=0.5))
    elements.append(d_line)
    elements.append(Spacer(1, 0.5*cm))
    
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=gris_medio)
    
    elements.append(Paragraph("¡Gracias por su visita!", 
        ParagraphStyle('Thanks', parent=style_footer, fontName='Helvetica-Bold', fontSize=10, textColor=gris_oscuro, spaceAfter=5)))
    
    elements.append(Paragraph('"Los Últimos Serán Los Primeros"', 
        ParagraphStyle('Slogan2', parent=style_footer, fontName='Helvetica-Oblique', fontSize=8, spaceAfter=2)))
        
    elements.append(Paragraph("HairSoft - Sistema de Gestión", style_footer))

    doc.build(elements)
    return buffer.getvalue()