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
from django.db.models import Sum
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
                    pass 
            
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
    
    # 🔥 MAGIA: Convertimos el formato de base de datos (YYYY-MM-DD) a formato latino (DD/MM/YYYY)
    try:
        f_inicio_str = datetime.strptime(str(fecha_inicio), '%Y-%m-%d').strftime('%d/%m/%Y')
        f_fin_str = datetime.strptime(str(fecha_fin), '%Y-%m-%d').strftime('%d/%m/%Y')
        periodo_texto = f"{f_inicio_str} al {f_fin_str}"
    except:
        periodo_texto = f"{fecha_inicio} al {fecha_fin}"
    
    col_der = [
        Paragraph(titulo_texto, estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(emisor_nombre, estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("PERÍODO", estilos['DatoDerL']),
        Paragraph(periodo_texto, estilos['DatoDerV']),
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
    for emp in data_empleados:
        grand_total += emp['total']
        elements.append(Paragraph(f"PROFESIONAL: {emp['nombre']}", estilos['Empresa']))
        
        # --- TABLA DE RESUMEN ---
        resumen_data = [
            [Paragraph("CONCEPTO", estilos['TH']), Paragraph("MONTO", estilos['TH'])],
        ]
        if emp['sueldo_fijo'] > 0:
            resumen_data.append([Paragraph("Sueldo Fijo", estilos['TD']), Paragraph(f"${emp['sueldo_fijo']:,.2f}", estilos['TD_Right'])])
        
        resumen_data.append([Paragraph("Comisiones Generadas", estilos['TD']), Paragraph(f"${emp['comisiones']:,.2f}", estilos['TD_Right'])])
        resumen_data.append([Paragraph("TOTAL A PAGAR", estilos['DatoDerV']), Paragraph(f"${emp['total']:,.2f}", estilos['DatoDerV'])])
        
        t_res = Table(resumen_data, colWidths=[12*cm, 7*cm])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(t_res)
        elements.append(Spacer(1, 15))

        # --- TABLA DE DETALLE DE TURNOS ---
        if emp.get('turnos'):
            elements.append(Paragraph("DETALLE DE SERVICIOS Y COMISIONES", ParagraphStyle('Subtit', fontName='Helvetica-Bold', fontSize=10, textColor=GRIS_TEXTO, spaceAfter=5)))
            
            detalles_data = [[
                Paragraph("FECHA", estilos['TH']),
                Paragraph("CLIENTE", estilos['TH']),
                Paragraph("SERVICIOS", estilos['TH']),
                Paragraph("COMISIÓN", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT))
            ]]
            
            for t in emp['turnos']:
                detalles_data.append([
                    Paragraph(t['fecha'], estilos['TD']),
                    Paragraph(t['cliente'], estilos['TD']),
                    Paragraph(t['servicios'], estilos['TD']),
                    Paragraph(f"${t['monto']:,.2f}", estilos['TD_Right'])
                ])
            
            t_det = Table(detalles_data, colWidths=[2.5*cm, 5.5*cm, 8*cm, 3*cm])
            t_det.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), GRIS_CLARO),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('TOPPADDING', (0,0), (-1,0), 6),
            ]))
            elements.append(t_det)
            
        elements.append(Spacer(1, 30))

    funcion_cierre = sello_pagado if es_pagado else footer
    doc.build(elements, onFirstPage=funcion_cierre, onLaterPages=funcion_cierre)
    return buffer.getvalue()

# ====================================================================
#  3. GENERAR REPORTE DE VENTAS (LISTADO)
# ====================================================================
def generar_reporte_ventas(ventas, filtros, usuario_impresor, config):
    import re
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from io import BytesIO
    from datetime import datetime

    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    def limpiar_texto(texto):
        if texto is None:
            return ""
        texto = str(texto)
        texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑ\s]', '', texto)
        return texto.strip()

    def formatear_fecha_filtro(fecha_str):
        if not fecha_str: return ""
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return fecha_str

    logo_img = obtener_logo_reporte(config)

    col_izq = [
        Paragraph(limpiar_texto(config.razon_social), estilos['Empresa']),
        Spacer(1, 4),
        Paragraph(f"<b>CUIT:</b> {limpiar_texto(config.cuil_cuit)}", estilos['DatosEmpresa']),
        Paragraph(f"<b>DIRECCIÓN:</b> {limpiar_texto(config.direccion)}", estilos['DatosEmpresa']),
        Paragraph(f"<b>TELÉFONO:</b> {limpiar_texto(config.telefono)}", estilos['DatosEmpresa']),
        Paragraph(f"<b>EMAIL:</b> {limpiar_texto(config.email)}", estilos['DatosEmpresa']),
    ]

    if logo_img:
        bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9.5*cm])
        bloque_izquierda.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0)]))
    else:
        bloque_izquierda = col_izq

    filtros_str = ""
    if filtros:
        f_list = []
        # ✅ AHORA FORMATEAMOS LAS FECHAS ANTES DE AGREGARLAS
        if filtros.get('fecha_desde'): 
            f_list.append(f"Desde: {formatear_fecha_filtro(filtros['fecha_desde'])}")
        if filtros.get('fecha_hasta'): 
            f_list.append(f"Hasta: {formatear_fecha_filtro(filtros['fecha_hasta'])}")
            
        if filtros.get('metodo_pago'): f_list.append(f"Método: {filtros['metodo_pago']}")
        if filtros.get('estado'): f_list.append(f"Estado: {filtros['estado']}")
        if f_list:
            filtros_str = " | ".join(f_list)

    col_der = [
        Paragraph("REPORTE DE VENTAS", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("EMITIDO POR", estilos['DatoDerL']),
        Paragraph(limpiar_texto(usuario_impresor), estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("FECHA EMISIÓN", estilos['DatoDerL']),
        Paragraph(datetime.now().strftime("%d/%m/%Y"), estilos['DatoDerV']),
    ]
    if filtros_str:
        col_der.extend([
            Spacer(1, 3),
            Paragraph("FILTROS APLICADOS", estilos['DatoDerL']),
            Paragraph(limpiar_texto(filtros_str), estilos['DatoDerV']),
        ])

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 1*cm))

    col_widths = [
        2.5*cm,  # FECHA
        4.8*cm,  # CLIENTE
        4.0*cm,  # USUARIO
        3.0*cm,  # MÉTODO
        2.0*cm,  # ESTADO
        2.7*cm,  # TOTAL
    ]

    rows = [[
        Paragraph("FECHA", estilos['TH']),
        Paragraph("CLIENTE", estilos['TH']),
        Paragraph("USUARIO", estilos['TH']),
        Paragraph("MÉTODO", estilos['TH']),
        Paragraph("ESTADO", estilos['TH']),
        Paragraph("TOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]

    total_general = 0
    filas_con_error = 0

    for v in ventas:
        try:
            fecha_str = v.fecha.strftime("%d/%m/%Y %H:%M") if v.fecha else "-"
            
            if v.cliente:
                nombre = limpiar_texto(v.cliente.nombre)
                apellido = limpiar_texto(v.cliente.apellido)
                cliente = f"{nombre} {apellido}".strip()
                if not cliente:
                    cliente = "Cliente sin nombre"
            else:
                cliente = "Venta Rápida"
            
            if v.usuario:
                nombre_u = limpiar_texto(v.usuario.nombre)
                apellido_u = limpiar_texto(v.usuario.apellido)
                usuario = f"{nombre_u} {apellido_u}".strip()
                if not usuario:
                    usuario = limpiar_texto(v.usuario.username) or "-"
            else:
                usuario = "-"
            
            metodo = limpiar_texto(v.medio_pago.nombre) if v.medio_pago else "-"
            estado = "ANULADA" if v.anulada else "ACTIVA"
            total = float(v.total) if v.total else 0
            total_general += total

            rows.append([
                Paragraph(fecha_str, estilos['TD']),
                Paragraph(cliente, estilos['TD']),
                Paragraph(usuario, estilos['TD']),
                Paragraph(metodo, estilos['TD']),
                Paragraph(estado, estilos['TD']),
                Paragraph(f"${total:,.2f}", estilos['TD_Right']),
            ])
        except Exception as e:
            filas_con_error += 1
            rows.append([
                Paragraph("ERROR", estilos['TD']),
                Paragraph("", estilos['TD']),
                Paragraph("", estilos['TD']),
                Paragraph("", estilos['TD']),
                Paragraph("", estilos['TD']),
                Paragraph("", estilos['TD']),
            ])
            continue

    rows.append([
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("TOTAL GENERAL", ParagraphStyle('TDBold', parent=estilos['TD'], fontName='Helvetica-Bold', alignment=TA_RIGHT)),
        Paragraph(f"${total_general:,.2f}", ParagraphStyle('TDBoldRight', parent=estilos['TD_Right'], fontName='Helvetica-Bold')),
    ])

    if filas_con_error > 0:
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f"Nota: {filas_con_error} fila(s) no pudieron procesarse correctamente.", 
                                   ParagraphStyle('Nota', parent=estilos['TD'], textColor=colors.red)))

    t_ventas = Table(rows, colWidths=col_widths)
    t_ventas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0,-1), (-1,-1), 1, AZUL_HEADER),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_ventas)

    try:
        doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    except Exception as e:
        error_buffer = BytesIO()
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(error_buffer, pagesize=A4)
        c.drawString(50, 800, f"Error al generar el reporte: {str(e)}")
        c.save()
        error_buffer.seek(0)
        return error_buffer.getvalue()

    buffer.seek(0)
    return buffer.getvalue()

def generar_comprobante_turno(turno):
    config = ConfiguracionSistema.get_solo()
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    logo_img = obtener_logo_reporte(config)
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

    col_der = [
        Paragraph("COMPROBANTE DE TURNO", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("NRO. TURNO", estilos['DatoDerL']),
        Paragraph(f"#{turno.id:06d}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("FECHA DEL TURNO", estilos['DatoDerL']),
        Paragraph(f"{turno.fecha.strftime('%d/%m/%Y')} {turno.hora.strftime('%H:%M')}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("CANAL", estilos['DatoDerL']),
        Paragraph(turno.get_canal_display(), estilos['DatoDerV']),
    ]

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 1*cm))

    cliente_nombre = f"{turno.cliente.nombre} {turno.cliente.apellido}" if turno.cliente else "Consumidor Final"
    peluquero_nombre = f"{turno.peluquero.nombre} {turno.peluquero.apellido}" if turno.peluquero else "-"
    
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    t_info = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(cliente_nombre, val_style)],
        [Paragraph("PELUQUERO", lbl_style), Paragraph(peluquero_nombre, val_style)],
        [Paragraph("ESTADO", lbl_style), Paragraph(turno.get_estado_display(), val_style)],
    ]], colWidths=[7*cm, 7*cm, 5*cm])
    
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), FONDO_ZEBRA),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 1*cm))

    rows = [[
        Paragraph("SERVICIO", estilos['TH']),
        Paragraph("DURACIÓN", estilos['TH']),
        Paragraph("PRECIO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    
    for s in turno.servicios.all():
        rows.append([
            Paragraph(s.nombre, estilos['TD']),
            Paragraph(f"{s.duracion} min", estilos['TD']),
            Paragraph(f"${s.precio:,.2f}", estilos['TD_Right']),
        ])

    t_items = Table(rows, colWidths=[11*cm, 4*cm, 4*cm])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(t_items)
    
    total_val = float(turno.monto_total) if turno.monto_total else sum(s.precio for s in turno.servicios.all())
    t_total = Table([
        [Paragraph("TOTAL DEL TURNO", estilos['TD_Right']), Paragraph(f"${total_val:,.2f}", estilos['DatoDerV'])]
    ], colWidths=[14*cm, 5*cm])
    elements.append(t_total)

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()

def generar_comprobante_pedido_web(pedido):
    config = ConfiguracionSistema.get_solo()
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    logo_img = obtener_logo_reporte(config)
    col_izq = [
        Paragraph(config.razon_social, estilos['Empresa']),
        Spacer(1, 4),
        Paragraph(f"<b>CUIT:</b> {config.cuil_cuit}", estilos['DatosEmpresa']),
        Paragraph(f"<b>TELÉFONO:</b> {config.telefono}", estilos['DatosEmpresa']),
    ]
    bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9.5*cm]) if logo_img else col_izq

    fecha_str = pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else datetime.now().strftime("%d/%m/%Y")

    col_der = [
        Paragraph("COMPROBANTE DE COMPRA", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("NRO. PEDIDO WEB", estilos['DatoDerL']),
        Paragraph(f"#{pedido.id:06d}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("FECHA", estilos['DatoDerL']),
        Paragraph(fecha_str, estilos['DatoDerV']),
    ]

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER), ('BOTTOMPADDING', (0,0), (-1,-1), 15)]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 1*cm))

    cliente_nombre = f"{pedido.cliente.nombre} {pedido.cliente.apellido}" if hasattr(pedido, 'cliente') and pedido.cliente else "Consumidor Final"
    tipo_entrega = getattr(pedido, 'tipo_entrega', 'RETIRO')
    
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    t_info = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(cliente_nombre, val_style)],
        [Paragraph("ENTREGA", lbl_style), Paragraph(tipo_entrega, val_style)],
        [Paragraph("ESTADO", lbl_style), Paragraph(pedido.estado, val_style)],
    ]], colWidths=[7*cm, 7*cm, 5*cm])
    t_info.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), FONDO_ZEBRA), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 10)]))
    elements.append(t_info)
    elements.append(Spacer(1, 1*cm))

    rows = [[
        Paragraph("PRODUCTO", estilos['TH']),
        Paragraph("CANT.", estilos['TH']),
        Paragraph("PRECIO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
        Paragraph("SUBTOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    
    for d in pedido.detalles.all():
        nombre_prod = getattr(d, 'nombre_producto', '') or (d.producto.nombre if hasattr(d, 'producto') and d.producto else 'Producto')
        rows.append([
            Paragraph(nombre_prod, estilos['TD']),
            Paragraph(str(d.cantidad), estilos['TD']),
            Paragraph(f"${d.precio_unitario:,.2f}", estilos['TD_Right']),
            Paragraph(f"${(d.cantidad * d.precio_unitario):,.2f}", estilos['TD_Right']),
        ])

    t_items = Table(rows, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
    t_items.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), AZUL_HEADER), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('GRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))]))
    elements.append(t_items)
    
    costo_envio = float(getattr(pedido, 'costo_envio', 0))
    if costo_envio > 0:
        elements.append(Table([[Paragraph("COSTO DE ENVÍO", estilos['TD_Right']), Paragraph(f"${costo_envio:,.2f}", estilos['DatoDerV'])]], colWidths=[14*cm, 5*cm]))
    
    elements.append(Table([[Paragraph("TOTAL", estilos['TD_Right']), Paragraph(f"${pedido.total:,.2f}", estilos['DatoDerV'])]], colWidths=[14*cm, 5*cm]))

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()

# ====================================================================
#  🔥 GENERAR CIERRE DE CAJA 🔥
# ====================================================================
def generar_cierre_caja_pdf(sesion, movimientos, config):
    buffer = BytesIO()
    estilos = get_estilos()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50)
    elements = []

    logo_img = obtener_logo_reporte(config)

    # --- HEADER EMPRESA ---
    col_izq = [
        Paragraph(config.razon_social, estilos['Empresa']),
        Spacer(1, 4),
        Paragraph(f"<b>CUIT:</b> {config.cuil_cuit}", estilos['DatosEmpresa']),
        Paragraph(f"<b>DIRECCIÓN:</b> {config.direccion}", estilos['DatosEmpresa']),
        Paragraph(f"<b>TELÉFONO:</b> {config.telefono}", estilos['DatosEmpresa']),
    ]
    bloque_izquierda = Table([[logo_img, col_izq]], colWidths=[2.5*cm, 9.5*cm]) if logo_img else col_izq

    # --- HEADER DATOS CAJA ---
    fecha_apertura = sesion.fecha_apertura.strftime("%d/%m/%Y %H:%M")
    fecha_cierre = sesion.fecha_cierre.strftime("%d/%m/%Y %H:%M") if sesion.fecha_cierre else "Sin cerrar"
    
    col_der = [
        Paragraph("PLANILLA DE ARQUEO", estilos['TituloDer']),
        Spacer(1, 6),
        Paragraph("SESIÓN NRO.", estilos['DatoDerL']),
        Paragraph(f"#{sesion.id:06d}", estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("APERTURA", estilos['DatoDerL']),
        Paragraph(fecha_apertura, estilos['DatoDerV']),
        Spacer(1, 3),
        Paragraph("CIERRE", estilos['DatoDerL']),
        Paragraph(fecha_cierre, estilos['DatoDerV']),
    ]

    tabla_header = Table([[bloque_izquierda, col_der]], colWidths=[12*cm, 7*cm])
    tabla_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LINEBELOW', (0,0), (-1,-1), 2, AZUL_HEADER), ('BOTTOMPADDING', (0,0), (-1,-1), 15)]))
    elements.append(tabla_header)
    elements.append(Spacer(1, 0.5*cm))

    # --- INFO DE USUARIOS ---
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    usuario_apertura = f"{sesion.usuario_apertura.nombre} {sesion.usuario_apertura.apellido}" if sesion.usuario_apertura else "Sistema"
    usuario_cierre = f"{sesion.usuario_cierre.nombre} {sesion.usuario_cierre.apellido}" if sesion.usuario_cierre else "Pendiente"

    t_usuarios = Table([[
        [Paragraph("CAJA", lbl_style), Paragraph(sesion.caja.nombre, val_style)],
        [Paragraph("USUARIO APERTURA", lbl_style), Paragraph(usuario_apertura, val_style)],
        [Paragraph("USUARIO CIERRE", lbl_style), Paragraph(usuario_cierre, val_style)],
    ]], colWidths=[6*cm, 7*cm, 6*cm])
    t_usuarios.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), FONDO_ZEBRA), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 10)]))
    elements.append(t_usuarios)
    elements.append(Spacer(1, 0.5*cm))

    # --- CÁLCULO DE BALANCE ---
    def sum_m(metodo, tipo): return movimientos.filter(metodo_pago=metodo, tipo=tipo).aggregate(t=Sum('monto'))['t'] or 0
    
    ing_ef = sum_m('EFECTIVO', 'INGRESO')
    egr_ef = sum_m('EFECTIVO', 'EGRESO')
    esp_ef = float(sesion.saldo_inicial_efectivo) + float(ing_ef) - float(egr_ef)
    real_ef = float(sesion.saldo_final_efectivo_real)

    ing_mp = sum_m('MERCADO_PAGO', 'INGRESO')
    egr_mp = sum_m('MERCADO_PAGO', 'EGRESO')
    esp_mp = float(sesion.saldo_inicial_mp) + float(ing_mp) - float(egr_mp)
    real_mp = float(sesion.saldo_final_mp_real)

    # Totales generales (NUEVO)
    total_esp = esp_ef + esp_mp
    total_real = real_ef + real_mp
    dif_total = total_real - total_esp

    # --- ESTILOS FIXEADOS (NO HEREDAN DE 'NORMAL') ---
    estilo_subtit = ParagraphStyle('Subtit', fontName='Helvetica-Bold', fontSize=12, textColor=AZUL_HEADER, spaceAfter=10)

    # --- RESUMEN DE SALDOS ---
    elements.append(Paragraph("RESUMEN CONTABLE", estilo_subtit))
    
    t_saldos = Table([
        [Paragraph("MEDIO", estilos['TH']), Paragraph("SISTEMA (ESPERADO)", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)), Paragraph("CAJERO (DECLARADO)", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)), Paragraph("DIFERENCIA", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT))],
        [Paragraph("Físico (Efectivo)", estilos['TD']), Paragraph(f"${esp_ef:,.2f}", estilos['TD_Right']), Paragraph(f"${real_ef:,.2f}", estilos['TD_Right']), Paragraph(f"${(real_ef - esp_ef):,.2f}", estilos['TD_Right'])],
        [Paragraph("Mercado Pago", estilos['TD']), Paragraph(f"${esp_mp:,.2f}", estilos['TD_Right']), Paragraph(f"${real_mp:,.2f}", estilos['TD_Right']), Paragraph(f"${(real_mp - esp_mp):,.2f}", estilos['TD_Right'])],
        
        # 🔥 NUEVA FILA DE TOTAL GENERAL
        [Paragraph("<b>TOTAL GENERAL</b>", estilos['TD']), Paragraph(f"<b>${total_esp:,.2f}</b>", estilos['TD_Right']), Paragraph(f"<b>${total_real:,.2f}</b>", estilos['TD_Right']), Paragraph(f"<b>${dif_total:,.2f}</b>", estilos['TD_Right'])],
    ], colWidths=[5*cm, 4.5*cm, 4.5*cm, 5*cm])
    
    # Le agregamos una línea gris arriba de la fila de total general para separarla
    t_saldos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_HEADER), 
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0,3), (-1,3), 1, colors.HexColor('#94a3b8')) # Línea separadora del Total
    ]))
    elements.append(t_saldos)
    
    # Diferencia total y Observaciones (Lo dejamos por si las moscas, aunque ya está en la tabla)
    if dif_total != 0:
        elements.append(Spacer(1, 0.3*cm))
        color_dif = colors.red if dif_total < 0 else colors.green
        estilo_dif = ParagraphStyle('Dif', fontName='Helvetica-Bold', textColor=color_dif)
        elements.append(Paragraph(f"DIFERENCIA TOTAL: ${dif_total:,.2f}", estilo_dif))
        
        if sesion.observaciones:
            elements.append(Paragraph(f"Justificación: {sesion.observaciones}", estilos['DatosEmpresa']))

    elements.append(Spacer(1, 0.8*cm))

    # --- MOVIMIENTOS ---
    elements.append(Paragraph("DETALLE DE MOVIMIENTOS", estilo_subtit))
    
    rows = [[Paragraph("HORA", estilos['TH']), Paragraph("TIPO", estilos['TH']), Paragraph("CONCEPTO Y DESCRIPCIÓN", estilos['TH']), Paragraph("MÉTODO", estilos['TH']), Paragraph("MONTO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT))]]
    
    for mov in movimientos:
        signo = "+" if mov.tipo == "INGRESO" else "-"
        
        # 🔥 NUEVO: Unificamos Concepto y Descripción en una sola celda
        texto_concepto = f"<b>{mov.get_concepto_display()}</b>"
        if mov.descripcion:
            texto_concepto += f"<br/><font color='#64748b' size='7'>{mov.descripcion}</font>"
            
        rows.append([
            Paragraph(mov.fecha.strftime("%H:%M"), estilos['TD']),
            Paragraph(mov.tipo, estilos['TD']),
            Paragraph(texto_concepto, estilos['TD']), # Acá mandamos el texto unificado
            Paragraph(mov.get_metodo_pago_display(), estilos['TD']),
            Paragraph(f"{signo}${mov.monto:,.2f}", estilos['TD_Right']),
        ])
    
    t_movs = Table(rows, colWidths=[2.5*cm, 2.5*cm, 7.5*cm, 3*cm, 3.5*cm])
    t_movs.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), AZUL_HEADER), ('GRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e2e8f0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(t_movs)

    elements.append(Spacer(1, 2*cm))

    # --- FIRMAS ---
    t_firmas = Table([
        [Paragraph("________________________________", ParagraphStyle('Firma', alignment=TA_CENTER)), Paragraph("________________________________", ParagraphStyle('Firma', alignment=TA_CENTER))],
        [Paragraph(f"Firma Usuario caja: {usuario_cierre}", ParagraphStyle('FirmaT', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9, textColor=GRIS_TEXTO)), Paragraph("Firma Administrador", ParagraphStyle('FirmaT', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9, textColor=GRIS_TEXTO))],
    ], colWidths=[9.5*cm, 9.5*cm])
    elements.append(t_firmas)

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()