from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import cm, mm
from io import BytesIO
from datetime import datetime
import os
import requests
from django.conf import settings
from .models import ConfiguracionSistema

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

def obtener_logo_reporte(config):
    try:
        if config.logo:
            if hasattr(config.logo, 'url'):
                try:
                    response = requests.get(config.logo.url, timeout=5)
                    if response.status_code == 200:
                        img_data = BytesIO(response.content)
                        return Image(img_data, width=2.2*cm, height=2.2*cm)
                except:
                    pass # Si falla el download, intenta local
            
            return Image(config.logo.path, width=2.2*cm, height=2.2*cm)
    except Exception as e:
        print(f"Error cargando logo dinámico: {e}")
    
    logo_path = os.path.join(settings.BASE_DIR, 'logo_barberia.jpg')
    if os.path.exists(logo_path):
        return Image(logo_path, width=2.2*cm, height=2.2*cm)
    return None

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GRIS_CLARO)
    width, height = A4
    canvas.drawCentredString(width / 2, 1.5 * cm, "HairSoft - Sistema de Gestión Integral")
    # ✅ PÁGINA AL FINAL A LA DERECHA
    canvas.drawRightString(width - 2 * cm, 1.5 * cm, f"Página {canvas.getPageNumber()}")
    canvas.restoreState()

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
    canvas.drawCentredString(0, -30, f"LIQUIDADO: {datetime.now().strftime('%d/%m/%Y')}")
    canvas.restoreState()

# ====================================================================
#  1. GENERAR COMPROBANTE DE VENTA
# ====================================================================
def generar_comprobante_venta(venta_data, detalles, usuario_impresor):
    config = ConfiguracionSistema.get_solo()
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    logo_img = obtener_logo_reporte(config)

    # ✅ COLUMNA IZQUIERDA: DATOS APILADOS UNO DEBAJO DEL OTRO
    col_izq = [
        Paragraph(config.razon_social, estilos['Empresa']),
        Spacer(1, 4),
        Paragraph(f"<b>CUIT:</b> {config.cuil_cuit}", estilos['DatosEmpresa']),
        Paragraph(f"<b>DIRECCIÓN:</b> {config.direccion}", estilos['DatosEmpresa']),
        Paragraph(f"<b>TELÉFONO:</b> {config.telefono}", estilos['DatosEmpresa']),
        Paragraph(f"<b>EMAIL:</b> {config.email}", estilos['DatosEmpresa']),
    ]

    if logo_img:
        bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9.5*cm])
        bloque_izquierda.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    else:
        bloque_izquierda = col_izq

    fecha_dt = datetime.now()
    if venta_data.get('fecha'):
        try:
            val = str(venta_data['fecha'])
            if 'T' in val: fecha_dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
            elif isinstance(venta_data['fecha'], datetime): fecha_dt = venta_data['fecha']
        except: pass
    
    emisor_nombre = usuario_impresor if usuario_impresor else "Sistema"

    # ✅ COLUMNA DERECHA: EMITIDO POR ARRIBA
    col_der = [
        Paragraph("COMPROBANTE DE VENTA", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(emisor_nombre, estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("NRO. COMPROBANTE", estilos['DatoDerL']),
        Paragraph(f"#{venta_data.get('id', 0):06d}", estilos['DatoDerV']),
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

    # --- LÓGICA DE CLIENTE Y TABLA (SIN CAMBIOS) ---
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
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 1*cm))

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
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(t_items)
    
    total_val = float(venta_data.get('total', 0))
    t_total = Table([[Paragraph("TOTAL A PAGAR", estilos['TD_Right']), Paragraph(f"${total_val:,.2f}", estilos['DatoDerV'])]], colWidths=[14*cm, 5*cm])
    elements.append(t_total)

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()

# ====================================================================
#  2. GENERAR LIQUIDACIÓN DE SUELDOS
# ====================================================================
def generar_liquidacion_pdf(data_empleados, fecha_inicio, fecha_fin, usuario_impresor, es_pagado=False):
    config = ConfiguracionSistema.get_solo()
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    logo_img = obtener_logo_reporte(config)

    # ✅ CABECERA STACKED PARA LIQUIDACIÓN
    col_izq = [
        Paragraph(config.razon_social, estilos['Empresa']),
        Spacer(1, 4),
        Paragraph(f"<b>CUIT:</b> {config.cuil_cuit}", estilos['DatosEmpresa']),
        Paragraph(f"<b>DIRECCIÓN:</b> {config.direccion}", estilos['DatosEmpresa']),
        Paragraph(f"<b>TELÉFONO:</b> {config.telefono}", estilos['DatosEmpresa']),
        Paragraph(f"<b>EMAIL:</b> {config.email}", estilos['DatosEmpresa']),
    ]

    if logo_img:
        bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9.5*cm])
        bloque_izquierda.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    else:
        bloque_izquierda = col_izq

    titulo_texto = "COMPROBANTE DE PAGO" if es_pagado else "LIQUIDACIÓN PRELIMINAR"
    emisor_nombre = usuario_impresor if usuario_impresor else "Sistema"
    
    col_der = [
        Paragraph(titulo_texto, estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(emisor_nombre, estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("PERÍODO", estilos['DatoDerL']),
        Paragraph(f"{fecha_inicio} al {fecha_fin}", estilos['DatoDerV']),
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

    # --- RESTO DE LA LÓGICA DE LIQUIDACIÓN (MANTENIDA) ---
    grand_total = 0
    for emp in data_empleados:
        grand_total += emp['total']
        elements.append(Paragraph(f"PROFESIONAL: {emp['nombre']}", estilos['Empresa']))
        resumen_data = [
            [Paragraph("CONCEPTO", estilos['TH']), Paragraph("MONTO", estilos['TH'])],
            [Paragraph("Comisiones", estilos['TD']), Paragraph(f"${emp['comisiones']:,.2f}", estilos['TD_Right'])],
            [Paragraph("Sueldo Fijo", estilos['TD']), Paragraph(f"${emp['sueldo_fijo']:,.2f}", estilos['TD_Right'])],
            [Paragraph("TOTAL", estilos['DatoDerV']), Paragraph(f"${emp['total']:,.2f}", estilos['DatoDerV'])]
        ]
        t_res = Table(resumen_data, colWidths=[12*cm, 7*cm])
        t_res.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), AZUL_HEADER)]))
        elements.append(t_res)
        elements.append(Spacer(1, 20))

    funcion_cierre = sello_pagado if es_pagado else footer
    doc.build(elements, onFirstPage=funcion_cierre, onLaterPages=funcion_cierre)
    return buffer.getvalue()