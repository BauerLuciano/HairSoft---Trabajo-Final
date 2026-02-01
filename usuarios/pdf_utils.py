from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import cm, mm
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

# --- DATOS DE LA EMPRESA (FIJOS POR PEDIDO DE CÁTEDRA) ---
DATOS_EMPRESA = {
    "razon_social": "Los Últimos Serán Los Primeros",
    "cuit": "27-23456789-3",
    "direccion": "Avenida Libertador 600, San Vicente - Misiones",
    "telefono": "3755 67-2716"
}

# --- CONFIGURACIÓN DE ESTILOS GLOBALES ---
AZUL_HEADER = colors.HexColor('#0f172a') 
GRIS_TEXTO = colors.HexColor('#334155')
GRIS_CLARO = colors.HexColor('#64748b')
FONDO_ZEBRA = colors.HexColor('#f8fafc')
BLANCO = colors.HexColor('#ffffff')
VERDE_EXITO = colors.HexColor('#10b981')

def get_estilos():
    styles = getSampleStyleSheet()
    return {
        'Empresa': ParagraphStyle('Empresa', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_HEADER, textTransform='uppercase', leading=13),
        'DatosEmpresa': ParagraphStyle('DatosEmpresa', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=GRIS_TEXTO, leading=12),
        'TituloDer': ParagraphStyle('TituloDer', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=AZUL_HEADER, alignment=TA_RIGHT, textTransform='uppercase', spaceAfter=5),
        'DatoDerL': ParagraphStyle('DatoDerL', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=GRIS_CLARO, alignment=TA_RIGHT, textTransform='uppercase'),
        'DatoDerV': ParagraphStyle('DatoDerV', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER, alignment=TA_RIGHT),
        'TH': ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, textColor=BLANCO),
        'TD': ParagraphStyle('TD', fontName='Helvetica', fontSize=9, textColor=GRIS_TEXTO),
        'TD_Right': ParagraphStyle('TD_Right', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=GRIS_TEXTO, alignment=TA_RIGHT),
    }

# Función para el Pie de Página (Numeración)
def footer(canvas, doc):
    canvas.saveState()
    font_name = 'Helvetica'
    font_size = 8
    canvas.setFont(font_name, font_size)
    canvas.setFillColor(GRIS_CLARO)

    width, height = A4

    # Frase HairSoft al centro
    text_footer = "HairSoft - Sistema de Gestión Integral"
    canvas.drawCentredString(width / 2, 1.5 * cm, text_footer)

    # Numeración a la derecha
    page_num = canvas.getPageNumber()
    text_page = f"Página {page_num}"
    canvas.drawRightString(width - 2 * cm, 1.5 * cm, text_page)

    canvas.restoreState()

# Función para el Sello de PAGADO
def sello_pagado(canvas, doc):
    footer(canvas, doc)
    
    canvas.saveState()
    canvas.translate(300, 400) 
    canvas.rotate(25) 
    c_rojo = colors.Color(0.8, 0, 0, alpha=0.3)
    canvas.setStrokeColor(c_rojo)
    canvas.setFillColor(c_rojo)
    canvas.setLineWidth(5)
    canvas.roundRect(-100, -40, 200, 80, 10, stroke=1, fill=0)
    canvas.setFont("Helvetica-Bold", 40)
    canvas.drawCentredString(0, -10, "PAGADO")
    canvas.setFont("Helvetica-Bold", 10)
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    canvas.drawCentredString(0, -30, f"LIQUIDADO: {fecha_hoy}")
    canvas.restoreState()

# ====================================================================
#  1. GENERAR COMPROBANTE DE VENTA
# ====================================================================
def generar_comprobante_venta(venta_data, detalles, usuario_impresor):
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    # --- ENCABEZADO ---
    logo_path = os.path.join(settings.BASE_DIR, 'logo_barberia.jpg')
    logo_img = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.2*cm, height=2.2*cm)
        logo.hAlign = 'LEFT'
        logo_img = logo

    col_izq = [
        Paragraph(DATOS_EMPRESA['razon_social'], estilos['Empresa']),
        Spacer(1, 3),
        Paragraph(f"<b>CUIT:</b> {DATOS_EMPRESA['cuit']}", estilos['DatosEmpresa']),
        Paragraph(f"<b>Dirección:</b> {DATOS_EMPRESA['direccion']}", estilos['DatosEmpresa']),
        Paragraph(f"<b>Teléfono:</b> {DATOS_EMPRESA['telefono']}", estilos['DatosEmpresa']),
    ]

    if logo_img:
        bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9*cm])
        bloque_izquierda.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    else:
        bloque_izquierda = col_izq

    # Fecha y Usuario
    fecha_dt = datetime.now()
    if venta_data.get('fecha'):
        try:
            val = str(venta_data['fecha'])
            if 'T' in val: fecha_dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
            elif isinstance(venta_data['fecha'], datetime): fecha_dt = venta_data['fecha']
        except: pass
    
    # Nombre del emisor (Usuario logueado)
    emisor_nombre = usuario_impresor if usuario_impresor else "Sistema"

    col_der = [
        Paragraph("COMPROBANTE DE VENTA", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("NRO. COMPROBANTE", estilos['DatoDerL']),
        Paragraph(f"#{venta_data.get('id', 0):06d}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(emisor_nombre, estilos['DatoDerV']), # AQUI SALE EL NOMBRE
        Spacer(1, 3),
        Paragraph("FECHA", estilos['DatoDerL']),
        Paragraph(fecha_dt.strftime("%d/%m/%Y"), estilos['DatoDerV']),
    ]

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 1*cm))

    # --- CLIENTE ---
    cliente = venta_data.get('cliente_nombre') or "Consumidor Final"
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    t_cliente = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(cliente, val_style)],
        [Paragraph("MEDIO DE PAGO", lbl_style), Paragraph(venta_data.get('medio_pago_nombre', 'Efectivo'), val_style)],
        [Paragraph("TIPO", lbl_style), Paragraph(venta_data.get('tipo', 'VENTA'), val_style)],
    ]], colWidths=[8*cm, 6*cm, 5*cm])
    
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), FONDO_ZEBRA),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]), 
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 1*cm))

    # --- ITEMS ---
    rows = [[
        Paragraph("DESCRIPCIÓN", estilos['TH']),
        Paragraph("CANT.", estilos['TH']),
        Paragraph("PRECIO UNIT.", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
        Paragraph("SUBTOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    
    for d in detalles:
        desc = "Item"
        if hasattr(d, 'producto') and d.producto: desc = d.producto.nombre
        elif hasattr(d, 'servicio') and d.servicio: desc = d.servicio.nombre
        elif hasattr(d, 'turno') and d.turno: desc = f"Servicio Turno #{d.turno.id}"
        
        rows.append([
            Paragraph(desc, estilos['TD']),
            Paragraph(str(int(d.cantidad)), estilos['TD']),
            Paragraph(f"${d.precio_unitario:,.2f}", estilos['TD_Right']),
            Paragraph(f"${d.subtotal:,.2f}", ParagraphStyle('TDB', parent=estilos['TD_Right'], fontName='Helvetica-Bold')),
        ])

    t_items = Table(rows, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
    table_styles = [
        ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (0,-1), 10),
        ('RIGHTPADDING', (-1,0), (-1,-1), 10),
    ]
    for i in range(1, len(rows)):
        bg = FONDO_ZEBRA if i % 2 == 0 else BLANCO
        table_styles.append(('BACKGROUND', (0,i), (-1,i), bg))
        table_styles.append(('LINEBELOW', (0,i), (-1,i), 0.5, colors.HexColor('#e2e8f0')))

    t_items.setStyle(TableStyle(table_styles))
    elements.append(t_items)
    elements.append(Spacer(1, 0.5*cm))

    # --- TOTAL ---
    total_val = float(venta_data.get('total', 0))
    total_lbl = ParagraphStyle('TL', fontName='Helvetica-Bold', fontSize=12, alignment=TA_RIGHT, textColor=GRIS_TEXTO)
    total_v = ParagraphStyle('TV', fontName='Helvetica-Bold', fontSize=16, alignment=TA_RIGHT, textColor=VERDE_EXITO)

    t_total = Table([[Paragraph("TOTAL A PAGAR", total_lbl), Paragraph(f"${total_val:,.2f}", total_v)]], colWidths=[14*cm, 5*cm])
    t_total.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 2, AZUL_HEADER), ('TOPPADDING', (0,0), (-1,-1), 12)]))
    elements.append(t_total)

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()

# ====================================================================
#  2. GENERAR LIQUIDACIÓN DE SUELDOS (AGREGADO USUARIO_IMPRESOR)
# ====================================================================
def generar_liquidacion_pdf(data_empleados, fecha_inicio, fecha_fin, usuario_impresor, es_pagado=False):
    """
    Genera el PDF de liquidación con datos fijos de empresa y usuario que imprime.
    """
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    # --- ENCABEZADO ---
    logo_path = os.path.join(settings.BASE_DIR, 'logo_barberia.jpg')
    logo_img = []
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.2*cm, height=2.2*cm)
        logo.hAlign = 'LEFT'
        logo_img = logo

    col_izq = [
        Paragraph(DATOS_EMPRESA['razon_social'], estilos['Empresa']),
        Spacer(1, 3),
        Paragraph(f"<b>CUIT:</b> {DATOS_EMPRESA['cuit']}", estilos['DatosEmpresa']),
        Paragraph(f"<b>Dirección:</b> {DATOS_EMPRESA['direccion']}", estilos['DatosEmpresa']),
        Paragraph(f"<b>Teléfono:</b> {DATOS_EMPRESA['telefono']}", estilos['DatosEmpresa']),
    ]

    if logo_img:
        bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9*cm])
        bloque_izquierda.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    else:
        bloque_izquierda = col_izq

    titulo_texto = "COMPROBANTE DE PAGO" if es_pagado else "LIQUIDACIÓN PRELIMINAR"
    emisor_nombre = usuario_impresor if usuario_impresor else "Sistema"
    
    col_der = [
        Paragraph(titulo_texto, estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("PERÍODO", estilos['DatoDerL']),
        Paragraph(f"{fecha_inicio} al {fecha_fin}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(emisor_nombre, estilos['DatoDerV']), # AQUI SALE EL NOMBRE
        Spacer(1, 3),
        Paragraph("FECHA EMISIÓN", estilos['DatoDerL']),
        Paragraph(datetime.now().strftime("%d/%m/%Y"), estilos['DatoDerV']),
    ]

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 1*cm))

    grand_total = 0

    if not data_empleados:
        elements.append(Paragraph("No hay datos para liquidar en este período.", estilos['TD']))

    for emp in data_empleados:
        grand_total += emp['total']
        
        # Título Empleado
        elements.append(Paragraph(f"PROFESIONAL: {emp['nombre']}", ParagraphStyle('EmpName', parent=estilos['Empresa'], fontSize=12)))
        elements.append(Spacer(1, 5))

        # Tabla Resumen (Sueldo + Comisiones)
        resumen_data = [
            [Paragraph("CONCEPTO", estilos['TH']), Paragraph("MONTO", estilos['TH'])],
            [Paragraph("Comisiones por Servicios", estilos['TD']), Paragraph(f"${emp['comisiones']:,.2f}", estilos['TD_Right'])]
        ]
        
        if emp['sueldo_fijo'] > 0:
            resumen_data.append([Paragraph("Sueldo Fijo / Base", estilos['TD']), Paragraph(f"${emp['sueldo_fijo']:,.2f}", estilos['TD_Right'])])
        
        # Fila Total Empleado
        total_emp_style = ParagraphStyle('TEmp', parent=estilos['DatoDerV'], color=VERDE_EXITO)
        resumen_data.append([Paragraph("TOTAL A PERCIBIR", ParagraphStyle('TEmpL', parent=estilos['DatoDerV'])), Paragraph(f"${emp['total']:,.2f}", total_emp_style)])

        t_res = Table(resumen_data, colWidths=[12*cm, 7*cm])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,1), (-1,-2), FONDO_ZEBRA),
            ('LINEBELOW', (0,-2), (-1,-2), 1, AZUL_HEADER), 
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_res)
        elements.append(Spacer(1, 10))

        # Tabla Detalle de Turnos (Si hay)
        if emp['turnos']:
            headers_det = [
                Paragraph("FECHA", estilos['TH']),
                Paragraph("CLIENTE", estilos['TH']),
                Paragraph("SERVICIOS", estilos['TH']),
                Paragraph("COMISIÓN", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
            ]
            rows_det = [headers_det]
            
            for t in emp['turnos']:
                rows_det.append([
                    Paragraph(t['fecha'], estilos['TD']),
                    Paragraph(t['cliente'], estilos['TD']),
                    Paragraph(t['servicios'], estilos['TD']),
                    Paragraph(f"${t['monto']:,.2f}", estilos['TD_Right']),
                ])
            
            t_det = Table(rows_det, colWidths=[2.5*cm, 4.5*cm, 9.5*cm, 2.5*cm])
            
            det_styles = [
                ('BACKGROUND', (0,0), (-1,0), GRIS_CLARO), 
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ]
            t_det.setStyle(TableStyle(det_styles))
            elements.append(t_det)
        
        elements.append(Spacer(1, 25))

    # Total General
    if grand_total > 0:
        t_grand = Table([[
            Paragraph("TOTAL GENERAL LIQUIDADO", estilos['TituloDer']), 
            Paragraph(f"${grand_total:,.2f}", ParagraphStyle('TGrand', parent=estilos['TituloDer'], textColor=VERDE_EXITO))
        ]], colWidths=[14*cm, 5*cm])
        elements.append(t_grand)

    # Función de cierre (Sello o Normal)
    funcion_cierre = sello_pagado if es_pagado else footer
    
    doc.build(elements, onFirstPage=funcion_cierre, onLaterPages=funcion_cierre)
    return buffer.getvalue()