from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime

def generar_comprobante_venta(venta_data, detalles):
    buffer = BytesIO()
    
    # --- Configuración del Documento ---
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()

    # --- ESTILOS PERSONALIZADOS ---
    
    # 1. Marca Principal (Título Grande)
    style_brand = ParagraphStyle(
        'Brand',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,      # Letra grande
        leading=32,       # ⚠️ FIX: Altura de línea para evitar solapamiento
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        spaceAfter=10     # Espacio extra abajo
    )
    
    # 2. Dirección (Texto gris pequeño)
    style_address = ParagraphStyle(
        'Address',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,       # Buen espaciado entre líneas
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_LEFT
    )

    # 3. Datos de la Factura (Derecha)
    style_invoice_title = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#2c3e50')
    )
    
    style_invoice_data = ParagraphStyle(
        'InvoiceData',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=14,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#34495e')
    )

    # 4. Texto Normal para Tablas
    style_cell_text = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2c3e50')
    )

    # --- 1. ENCABEZADO ---
    
    # Bloque Izquierdo: Título y Dirección
    # Usamos <br/> para asegurar saltos de línea limpios
    direccion_texto = """
    Avenida Libertador 600<br/>
    Galería Rosa - Local 3<br/>
    Tel: (3755) 12-3456<br/>
    Los Ultimos Serán Los Primeros<br/>
    Email: contacto@hairsoft.com
    """
    
    empresa_info = [
        Paragraph("HAIRSOFT", style_brand),
        Paragraph(direccion_texto, style_address)
    ]

    # Bloque Derecho: Datos de la Venta
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Manejo seguro de la fecha de venta
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

    comprobante_info = [
        Paragraph("COMPROBANTE DE VENTA", style_invoice_title),
        Paragraph("(NO FISCAL)", ParagraphStyle('NoFiscal', parent=style_invoice_title, fontSize=10, textColor=colors.red)),
        Spacer(1, 15),
        Paragraph(f"N° Venta: {venta_data.get('id', '000')}", style_invoice_data),
        Paragraph(f"Fecha: {fecha_texto}", style_invoice_data),
    ]

    # Tabla Maestra del Encabezado
    header_table = Table([
        [empresa_info, comprobante_info]
    ], colWidths=[11*cm, 7.5*cm])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'), # Alinear todo arriba
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # Línea separadora elegante
    d = Drawing(500, 1)
    d.add(Line(0, 0, 535, 0, strokeColor=colors.HexColor('#ecf0f1'), strokeWidth=2))
    elements.append(d)
    elements.append(Spacer(1, 1*cm))

    # --- 2. INFORMACIÓN DEL CLIENTE (Estilo Tarjeta) ---
    
    cliente_nombre = venta_data.get('cliente_nombre') or "Consumidor Final"
    usuario_vendedor = venta_data.get('usuario_nombre') or "Sistema"
    medio_pago = venta_data.get('medio_pago_nombre') or 'Efectivo'

    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", ParagraphStyle('SectionHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#7f8c8d'), spaceAfter=5)))

    # Tabla de datos del cliente con fondo gris
    datos_cliente = [
        [Paragraph("<b>Cliente:</b>", style_cell_text), Paragraph(cliente_nombre, style_cell_text)],
        [Paragraph("<b>Atendido por:</b>", style_cell_text), Paragraph(usuario_vendedor, style_cell_text)],
        [Paragraph("<b>Método de Pago:</b>", style_cell_text), Paragraph(medio_pago, style_cell_text)],
    ]

    tabla_cliente = Table(datos_cliente, colWidths=[4*cm, 14.5*cm])
    tabla_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')), # Fondo sutil
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        # Borde izquierdo decorativo
        ('LINEBEFORE', (0,0), (0,-1), 4, colors.HexColor('#2c3e50')), 
    ]))
    
    elements.append(tabla_cliente)
    elements.append(Spacer(1, 1*cm))

    # --- 3. DETALLE DE ITEMS ---
    
    # Encabezados
    data_items = [[
        Paragraph('<b>PRODUCTO / SERVICIO</b>', ParagraphStyle('TH', parent=style_cell_text, textColor=colors.white, alignment=TA_LEFT)),
        Paragraph('<b>CANT.</b>', ParagraphStyle('TH_C', parent=style_cell_text, textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('<b>PRECIO UNIT.</b>', ParagraphStyle('TH_R', parent=style_cell_text, textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph('<b>SUBTOTAL</b>', ParagraphStyle('TH_R', parent=style_cell_text, textColor=colors.white, alignment=TA_RIGHT)),
    ]]
    
    # Filas
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

        data_items.append([
            Paragraph(nombre, style_cell_text),
            Paragraph(str(detalle.cantidad), ParagraphStyle('CellC', parent=style_cell_text, alignment=TA_CENTER)),
            Paragraph(precio_fmt, ParagraphStyle('CellR', parent=style_cell_text, alignment=TA_RIGHT)),
            Paragraph(subtotal_fmt, ParagraphStyle('CellR', parent=style_cell_text, alignment=TA_RIGHT)),
        ])

    tabla_items = Table(data_items, colWidths=[9*cm, 2.5*cm, 3.5*cm, 3.5*cm])
    
    estilo_tabla = TableStyle([
        # Encabezado
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        
        # Cuerpo
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#ecf0f1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])
    
    tabla_items.setStyle(estilo_tabla)
    elements.append(tabla_items)
    elements.append(Spacer(1, 0.5*cm))

    # --- 4. TOTALES ---
    
    total_final = float(venta_data.get('total', 0))
    
    style_total_label = ParagraphStyle('TotalLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_RIGHT)
    style_total_value = ParagraphStyle('TotalValue', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=TA_RIGHT, textColor=colors.HexColor('#27ae60'))

    tabla_totales = Table([
        [Paragraph("TOTAL A PAGAR:", style_total_label), Paragraph(f"${total_final:,.2f}", style_total_value)]
    ], colWidths=[13.5*cm, 5*cm])
    
    tabla_totales.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.black), # Línea negra gruesa arriba del total
    ]))
    
    elements.append(tabla_totales)
    elements.append(Spacer(1, 2.5*cm))

    # --- 5. FOOTER ---
    
    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.gray
    )
    
    elements.append(Paragraph("<b>¡Gracias por confiar en nosotros!</b>", 
        ParagraphStyle('Thanks', parent=style_footer, fontSize=12, textColor=colors.HexColor('#2c3e50'), spaceAfter=8)))
    
    elements.append(Paragraph("Este documento no es válido como factura fiscal.", style_footer))
    elements.append(Paragraph("HairSoft - Sistema de Gestión de Peluquerías", 
        ParagraphStyle('SmallFooter', parent=style_footer, fontSize=7, spaceBefore=2)))
    elements.append(Paragraph("Los Ultimos Serán Los Primeros", 
        ParagraphStyle('SmallFooter', parent=style_footer, fontSize=7, spaceBefore=2)))

    # Generar PDF
    doc.build(elements)
    return buffer.getvalue()