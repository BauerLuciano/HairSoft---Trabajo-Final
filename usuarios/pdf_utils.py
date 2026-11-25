"""Generadores PDF de HairSoft.

Todos los documentos usan los helpers institucionales de `pdf_institucional`:
la empresa se lee siempre de ConfiguracionSistema, la emisión se registra una
sola vez y el pie.numera "Página X de Y" con el total real de páginas.
"""
import re
from datetime import datetime
from io import BytesIO

from django.db.models import Sum
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from .pdf_institucional import (
    AZUL_CLARO,
    AZUL_HEADER,
    BLANCO,
    FONDO_ZEBRA,
    GENERACION_AUTOMATICA,
    GRIS_CLARO,
    GRIS_TEXTO,
    NARANJA,
    ROJO,
    VERDE_EXITO,
    construir_documento,
    construir_encabezado,
    crear_documento,
    crear_grafico_barras,
    crear_grafico_dona,
    crear_grafico_lineas,
    crear_tabla_datos,
    dibujar_pie,
    escapar,
    formato_moneda_arg,
    formato_moneda_compacta_arg,
    formato_numero_arg,
    formatear_fecha_filtro,
    formatear_fecha_operacion,
    generar_pdf_error as _generar_pdf_error_institucional,
    get_estilos as _get_estilos,
    obtener_configuracion,
    obtener_datos_emision,
    obtener_logo_reporte as _obtener_logo_reporte,
    sello_pagado as _sello_pagado,
    solicitante_emision,
)

# Re-exportados para compatibilidad con código existente.
get_estilos = _get_estilos
obtener_logo_reporte = _obtener_logo_reporte


def footer(canvas_obj, doc):
    """Pie institucional simple (compatibilidad)."""
    dibujar_pie(canvas_obj, doc, 1)


def sello_pagado(canvas_obj, doc, fecha_liquidacion=None):
    """Sello PAGADO usando la fecha de emisión ya capturada."""
    _sello_pagado(canvas_obj, doc, fecha_liquidacion)


def limpiar_texto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑ\s]', '', texto)
    return texto.strip()


def _formato_numero(valor):
    return formato_numero_arg(valor)


def _formato_moneda(valor):
    return formato_moneda_arg(valor)


def formatear_periodo_balance(filtros=None):
    filtros = filtros or {}
    if filtros.get('date_from') and filtros.get('date_to'):
        return (
            f"{formatear_fecha_filtro(filtros['date_from'])} al "
            f"{formatear_fecha_filtro(filtros['date_to'])}"
        )
    etiquetas = {'hoy': 'Hoy', 'semana': '7 Días', 'mes': 'Este Mes'}
    periodo = filtros.get('period') or 'semana'
    return etiquetas.get(periodo, '7 Días')


# ====================================================================
#  1. COMPROBANTE DE VENTA
# ====================================================================
def generar_comprobante_venta(venta_data, detalles, datos_emision=None):
    config = obtener_configuracion()
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    fecha_operacion = formatear_fecha_operacion(
        venta_data.get('fecha') or datetime.now(), con_hora=True
    )
    encabezado = construir_encabezado(config, 'COMPROBANTE DE VENTA', [
        ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ('NRO. COMPROBANTE', f"#{venta_data.get('id', 0):06d}"),
        ('FECHA OPERACIÓN', fecha_operacion),
        ('FECHA EMISIÓN', datos_emision['fecha_emision']),
    ], estilos)

    elementos = [encabezado, Spacer(1, 1 * cm)]

    cliente = venta_data.get('cliente_nombre') or "Consumidor Final"
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    t_cliente = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(escapar(cliente), val_style)],
        [Paragraph("MEDIO DE PAGO", lbl_style), Paragraph(escapar(venta_data.get('medio_pago_nombre', 'Efectivo')), val_style)],
        [Paragraph("TIPO", lbl_style), Paragraph(escapar(venta_data.get('tipo', 'VENTA')), val_style)],
    ]], colWidths=[8 * cm, 6 * cm, 5 * cm])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_cliente)
    elementos.append(Spacer(1, 1 * cm))

    rows = [[
        Paragraph("DESCRIPCIÓN", estilos['TH']),
        Paragraph("CANT.", estilos['TH']),
        Paragraph("PRECIO UNIT.", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
        Paragraph("SUBTOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]

    for d in detalles:
        desc = "Item"
        if hasattr(d, 'producto') and d.producto:
            desc = d.producto.nombre
        elif hasattr(d, 'servicio') and d.servicio:
            desc = d.servicio.nombre
        elif hasattr(d, 'turno') and d.turno:
            desc = f"Servicio Turno #{d.turno.id}"

        rows.append([
            Paragraph(escapar(desc), estilos['TD']),
            Paragraph(str(int(d.cantidad)), estilos['TD']),
            Paragraph(f"${d.precio_unitario:,.2f}", estilos['TD_Right']),
            Paragraph(f"${d.subtotal:,.2f}", ParagraphStyle('TDB', parent=estilos['TD_Right'], fontName='Helvetica-Bold')),
        ])

    t_items = Table(rows, colWidths=[9 * cm, 2 * cm, 4 * cm, 4 * cm])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elementos.append(t_items)

    total_val = float(venta_data.get('total', 0))
    t_total = Table(
        [[Paragraph("TOTAL A PAGAR", estilos['TD_Right']), Paragraph(f"${total_val:,.2f}", estilos['DatoDerV'])]],
        colWidths=[14 * cm, 5 * cm],
    )
    elementos.append(t_total)

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


# ====================================================================
#  2. LIQUIDACIÓN DE SUELDOS
# ====================================================================
def generar_liquidacion_pdf(data_empleados, fecha_inicio, fecha_fin, datos_emision=None, es_pagado=False):
    config = obtener_configuracion()
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    periodo_texto = f"{formatear_fecha_filtro(fecha_inicio)} al {formatear_fecha_filtro(fecha_fin)}"
    elementos = [
        construir_encabezado(
            config,
            'COMPROBANTE DE PAGO' if es_pagado else 'LIQUIDACIÓN PRELIMINAR',
            [
                ('SOLICITADO POR', solicitante_emision(datos_emision)),
                ('PERÍODO', periodo_texto),
                ('FECHA EMISIÓN', datos_emision['fecha_emision']),
            ],
            estilos,
        ),
        Spacer(1, 1 * cm),
    ]

    for emp in data_empleados:
        elementos.append(Paragraph(f"PROFESIONAL: {escapar(emp['nombre'])}", estilos['Empresa']))

        resumen_data = [[Paragraph("CONCEPTO", estilos['TH']), Paragraph("MONTO", estilos['TH'])]]
        if emp['sueldo_fijo'] > 0:
            resumen_data.append([
                Paragraph("Sueldo Fijo", estilos['TD']),
                Paragraph(f"${emp['sueldo_fijo']:,.2f}", estilos['TD_Right']),
            ])
        resumen_data.append([
            Paragraph("Comisiones Generadas", estilos['TD']),
            Paragraph(f"${emp['comisiones']:,.2f}", estilos['TD_Right']),
        ])
        resumen_data.append([
            Paragraph("TOTAL A PAGAR", estilos['DatoDerV']),
            Paragraph(f"${emp['total']:,.2f}", estilos['DatoDerV']),
        ])

        t_res = Table(resumen_data, colWidths=[12 * cm, 7 * cm])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elementos.append(t_res)
        elementos.append(Spacer(1, 15))

        if emp.get('turnos'):
            elementos.append(Paragraph(
                "DETALLE DE SERVICIOS Y COMISIONES",
                ParagraphStyle('Subtit', fontName='Helvetica-Bold', fontSize=10, textColor=GRIS_TEXTO, spaceAfter=5),
            ))
            detalles_data = [[
                Paragraph("FECHA", estilos['TH']),
                Paragraph("CLIENTE", estilos['TH']),
                Paragraph("SERVICIOS", estilos['TH']),
                Paragraph("COMISIÓN", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
            ]]
            for t in emp['turnos']:
                servicios = escapar(t['servicios']).replace('&lt;br/&gt;', '<br/>')
                detalles_data.append([
                    Paragraph(escapar(t['fecha']), estilos['TD']),
                    Paragraph(escapar(t['cliente']), estilos['TD']),
                    Paragraph(servicios, estilos['TD']),
                    Paragraph(f"${t['monto']:,.2f}", estilos['TD_Right']),
                ])
            t_det = Table(detalles_data, colWidths=[2.5 * cm, 5.5 * cm, 8 * cm, 3 * cm])
            t_det.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), GRIS_CLARO),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
            ]))
            elementos.append(t_det)

        elementos.append(Spacer(1, 30))

    construir_documento(
        crear_documento(buffer),
        elementos,
        sello_liquidado=datos_emision['fecha_emision'] if es_pagado else None,
    )
    return buffer.getvalue()


# ====================================================================
#  3. REPORTE / LISTADO DE VENTAS
# ====================================================================
def generar_reporte_ventas(ventas, filtros, datos_emision=None, config=None):
    config = obtener_configuracion(config)
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    filtros_str = ""
    if filtros:
        partes = []
        if filtros.get('fecha_desde'):
            partes.append(f"Desde: {formatear_fecha_filtro(filtros['fecha_desde'])}")
        if filtros.get('fecha_hasta'):
            partes.append(f"Hasta: {formatear_fecha_filtro(filtros['fecha_hasta'])}")
        if filtros.get('metodo_pago'):
            partes.append(f"Método: {filtros['metodo_pago']}")
        if filtros.get('tipo'):
            partes.append(f"Tipo: {filtros['tipo']}")
        if filtros.get('estado'):
            partes.append(f"Estado: {filtros['estado']}")
        filtros_str = " | ".join(partes)

    pares = [
        ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ('FECHA EMISIÓN', datos_emision['fecha_emision']),
    ]
    if filtros_str:
        pares.append(('FILTROS APLICADOS', filtros_str))

    elementos = [
        construir_encabezado(config, 'REPORTE DE VENTAS', pares, estilos),
        Spacer(1, 1 * cm),
    ]

    col_widths = [2.5 * cm, 4.8 * cm, 4.0 * cm, 3.0 * cm, 2.0 * cm, 2.7 * cm]
    rows = [[
        Paragraph("FECHA", estilos['TH']),
        Paragraph("CLIENTE", estilos['TH']),
        Paragraph("OPERADOR", estilos['TH']),
        Paragraph("MÉTODO", estilos['TH']),
        Paragraph("ESTADO", estilos['TH']),
        Paragraph("TOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]

    total_general = 0
    filas_con_error = 0
    for v in ventas:
        try:
            fecha_str = formatear_fecha_operacion(v.fecha, con_hora=True) if v.fecha else "-"
            if v.cliente:
                nombre = limpiar_texto(v.cliente.nombre)
                apellido = limpiar_texto(v.cliente.apellido)
                cliente = f"{nombre} {apellido}".strip() or "Cliente sin nombre"
            else:
                cliente = "Venta Rápida"
            if v.usuario:
                nombre_u = limpiar_texto(v.usuario.nombre)
                apellido_u = limpiar_texto(v.usuario.apellido)
                usuario = f"{nombre_u} {apellido_u}".strip() or limpiar_texto(getattr(v.usuario, 'username', '')) or "-"
            else:
                usuario = "-"
            metodo = limpiar_texto(v.medio_pago.nombre) if v.medio_pago else "-"
            estado = "ANULADA" if v.anulada else "ACTIVA"
            total = float(v.total) if v.total else 0
            total_general += total
            rows.append([
                Paragraph(escapar(fecha_str), estilos['TD']),
                Paragraph(escapar(cliente), estilos['TD']),
                Paragraph(escapar(usuario), estilos['TD']),
                Paragraph(escapar(metodo), estilos['TD']),
                Paragraph(escapar(estado), estilos['TD']),
                Paragraph(f"${total:,.2f}", estilos['TD_Right']),
            ])
        except Exception:
            filas_con_error += 1
            rows.append([Paragraph("ERROR", estilos['TD'])] + [Paragraph("", estilos['TD'])] * 5)

    rows.append([
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("", estilos['TD']),
        Paragraph("TOTAL GENERAL", ParagraphStyle('TDBold', parent=estilos['TD'], fontName='Helvetica-Bold', alignment=TA_RIGHT)),
        Paragraph(f"${total_general:,.2f}", ParagraphStyle('TDBoldRight', parent=estilos['TD_Right'], fontName='Helvetica-Bold')),
    ])

    if filas_con_error > 0:
        elementos.append(Spacer(1, 0.5 * cm))
        elementos.append(Paragraph(
            f"Nota: {filas_con_error} fila(s) no pudieron procesarse correctamente.",
            ParagraphStyle('Nota', parent=estilos['TD'], textColor=colors.red),
        ))

    t_ventas = Table(rows, colWidths=col_widths, repeatRows=1)
    t_ventas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, AZUL_HEADER),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elementos.append(t_ventas)

    try:
        construir_documento(crear_documento(buffer), elementos)
    except Exception as exc:
        return _generar_pdf_error_institucional(
            f"Error al generar el reporte: {str(exc)}", config, datos_emision
        )
    return buffer.getvalue()


# ====================================================================
#  4. COMPROBANTE DE TURNO
# ====================================================================
def generar_comprobante_turno(turno, datos_emision=None):
    config = obtener_configuracion()
    # Sin solicitud HTTP, el documento se genera como proceso automático.
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    fecha_turno = (
        f"{formatear_fecha_operacion(turno.fecha, con_hora=False)} "
        f"{formatear_fecha_operacion(turno.hora, con_hora=False)}"
        if turno.fecha and turno.hora else '-'
    )
    elementos = [
        construir_encabezado(config, 'COMPROBANTE DE TURNO', [
            ('NRO. TURNO', f"#{turno.id:06d}"),
            ('FECHA DEL TURNO', fecha_turno),
            ('CANAL', turno.get_canal_display()),
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ], estilos),
        Spacer(1, 1 * cm),
    ]

    cliente_nombre = f"{turno.cliente.nombre} {turno.cliente.apellido}" if turno.cliente else "Consumidor Final"
    peluquero_nombre = f"{turno.peluquero.nombre} {turno.peluquero.apellido}" if turno.peluquero else "-"
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)

    t_info = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(escapar(cliente_nombre), val_style)],
        [Paragraph("PROFESIONAL", lbl_style), Paragraph(escapar(peluquero_nombre), val_style)],
        [Paragraph("ESTADO", lbl_style), Paragraph(escapar(turno.get_estado_display()), val_style)],
    ]], colWidths=[7 * cm, 7 * cm, 5 * cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_info)
    elementos.append(Spacer(1, 1 * cm))

    rows = [[
        Paragraph("SERVICIO", estilos['TH']),
        Paragraph("DURACIÓN", estilos['TH']),
        Paragraph("PRECIO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    for s in turno.servicios.all():
        rows.append([
            Paragraph(escapar(s.nombre), estilos['TD']),
            Paragraph(f"{s.duracion} min", estilos['TD']),
            Paragraph(f"${s.precio:,.2f}", estilos['TD_Right']),
        ])
    t_items = Table(rows, colWidths=[11 * cm, 4 * cm, 4 * cm])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elementos.append(t_items)

    total_val = float(turno.monto_total) if turno.monto_total else sum(s.precio for s in turno.servicios.all())
    es_sena = turno.tipo_pago == 'SENA_50'
    seña_val = float(turno.monto_seña) if turno.monto_seña else 0
    saldo_val = total_val - seña_val if es_sena else 0
    if es_sena and seña_val > 0:
        t_resumen = Table([
            [Paragraph("SUBTOTAL", estilos['TD_Right']), Paragraph(f"${total_val:,.2f}", estilos['TD_Right'])],
            [Paragraph("SEÑA ABONADA (50%)", ParagraphStyle('TR', parent=estilos['TD_Right'], textColor=colors.HexColor('#059669'))), Paragraph(f"${seña_val:,.2f}", ParagraphStyle('TRV', parent=estilos['DatoDerV'], textColor=colors.HexColor('#059669')))],
            [Paragraph("SALDO PENDIENTE", ParagraphStyle('TR', parent=estilos['TD_Right'], textColor=colors.HexColor('#dc2626'))), Paragraph(f"${saldo_val:,.2f}", ParagraphStyle('TRV', parent=estilos['DatoDerV'], textColor=colors.HexColor('#dc2626')))],
        ], colWidths=[14 * cm, 5 * cm])
        t_resumen.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#e2e8f0')),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(t_resumen)

    elementos.append(Table([
        [Paragraph("TOTAL DEL TURNO", estilos['TD_Right']), Paragraph(f"${total_val:,.2f}", estilos['DatoDerV'])]
    ], colWidths=[14 * cm, 5 * cm]))

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


# ====================================================================
#  5. COMPROBANTE DE PEDIDO WEB
# ====================================================================
def generar_comprobante_pedido_web(pedido, datos_emision=None):
    config = obtener_configuracion()
    # Sin solicitud HTTP, el documento se genera como proceso automático.
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    fecha_operacion = formatear_fecha_operacion(pedido.fecha_creacion, con_hora=True)
    tipo_entrega = (
        pedido.get_tipo_entrega_display() if hasattr(pedido, 'get_tipo_entrega_display')
        else getattr(pedido, 'tipo_entrega', '-')
    )
    estado = (
        pedido.get_estado_display() if hasattr(pedido, 'get_estado_display')
        else getattr(pedido, 'estado', '-')
    )
    elementos = [
        construir_encabezado(config, 'COMPROBANTE DE COMPRA', [
            ('NRO. PEDIDO WEB', f"#{pedido.id:06d}"),
            ('FECHA OPERACIÓN', fecha_operacion),
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ], estilos),
        Spacer(1, 1 * cm),
    ]

    cliente_nombre = f"{pedido.cliente.nombre} {pedido.cliente.apellido}" if hasattr(pedido, 'cliente') and pedido.cliente else "Consumidor Final"
    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)
    t_info = Table([[
        [Paragraph("CLIENTE", lbl_style), Paragraph(escapar(cliente_nombre), val_style)],
        [Paragraph("ENTREGA", lbl_style), Paragraph(escapar(tipo_entrega), val_style)],
        [Paragraph("ESTADO", lbl_style), Paragraph(escapar(estado), val_style)],
    ]], colWidths=[7 * cm, 7 * cm, 5 * cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_info)
    elementos.append(Spacer(1, 1 * cm))

    rows = [[
        Paragraph("PRODUCTO", estilos['TH']),
        Paragraph("CANT.", estilos['TH']),
        Paragraph("PRECIO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
        Paragraph("SUBTOTAL", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    for d in pedido.detalles.all():
        nombre_prod = getattr(d, 'nombre_producto', '') or (d.producto.nombre if hasattr(d, 'producto') and d.producto else 'Producto')
        rows.append([
            Paragraph(escapar(nombre_prod), estilos['TD']),
            Paragraph(str(d.cantidad), estilos['TD']),
            Paragraph(f"${d.precio_unitario:,.2f}", estilos['TD_Right']),
            Paragraph(f"${(d.cantidad * d.precio_unitario):,.2f}", estilos['TD_Right']),
        ])
    t_items = Table(rows, colWidths=[9 * cm, 2 * cm, 4 * cm, 4 * cm])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elementos.append(t_items)

    costo_envio = float(getattr(pedido, 'costo_envio', 0) or 0)
    if costo_envio > 0:
        elementos.append(Table([
            [Paragraph("COSTO DE ENVÍO", estilos['TD_Right']), Paragraph(f"${costo_envio:,.2f}", estilos['DatoDerV'])]
        ], colWidths=[14 * cm, 5 * cm]))
    elementos.append(Table([
        [Paragraph("TOTAL", estilos['TD_Right']), Paragraph(f"${pedido.total:,.2f}", estilos['DatoDerV'])]
    ], colWidths=[14 * cm, 5 * cm]))

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


# ====================================================================
#  6. ARQUEO / CIERRE DE CAJA
# ====================================================================
def generar_cierre_caja_pdf(sesion, movimientos, config=None, datos_emision=None):
    config = obtener_configuracion(config)
    datos_emision = datos_emision or obtener_datos_emision(None)
    buffer = BytesIO()
    estilos = get_estilos()

    elementos = [
        construir_encabezado(config, 'PLANILLA DE ARQUEO', [
            ('SESIÓN NRO.', f"#{sesion.id:06d}"),
            ('APERTURA', formatear_fecha_operacion(sesion.fecha_apertura, con_hora=True)),
            ('CIERRE', formatear_fecha_operacion(sesion.fecha_cierre, con_hora=True) if sesion.fecha_cierre else 'Sin cerrar'),
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ], estilos),
        Spacer(1, 0.5 * cm),
    ]

    lbl_style = ParagraphStyle('L', fontSize=8, textColor=GRIS_CLARO, textTransform='uppercase')
    val_style = ParagraphStyle('V', fontName='Helvetica-Bold', fontSize=10, textColor=AZUL_HEADER)
    usuario_apertura = f"{sesion.usuario_apertura.nombre} {sesion.usuario_apertura.apellido}" if sesion.usuario_apertura else "Sistema"
    usuario_cierre = f"{sesion.usuario_cierre.nombre} {sesion.usuario_cierre.apellido}" if sesion.usuario_cierre else "Pendiente"
    t_usuarios = Table([[
        [Paragraph("CAJA", lbl_style), Paragraph(escapar(sesion.caja.nombre), val_style)],
        [Paragraph("OPERADOR APERTURA", lbl_style), Paragraph(escapar(usuario_apertura), val_style)],
        [Paragraph("OPERADOR CIERRE", lbl_style), Paragraph(escapar(usuario_cierre), val_style)],
    ]], colWidths=[6 * cm, 7 * cm, 6 * cm])
    t_usuarios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(t_usuarios)
    elementos.append(Spacer(1, 0.5 * cm))

    def sum_m(metodo, tipo):
        return movimientos.filter(metodo_pago=metodo, tipo=tipo).aggregate(t=Sum('monto'))['t'] or 0

    ing_ef = sum_m('EFECTIVO', 'INGRESO')
    egr_ef = sum_m('EFECTIVO', 'EGRESO')
    esp_ef = float(sesion.saldo_inicial_efectivo) + float(ing_ef) - float(egr_ef)
    real_ef = float(sesion.saldo_final_efectivo_real or 0)
    ing_mp = sum_m('MERCADO_PAGO', 'INGRESO')
    egr_mp = sum_m('MERCADO_PAGO', 'EGRESO')
    esp_mp = float(sesion.saldo_inicial_mp) + float(ing_mp) - float(egr_mp)
    real_mp = float(sesion.saldo_final_mp_real or 0)
    total_esp = esp_ef + esp_mp
    total_real = real_ef + real_mp
    dif_total = total_real - total_esp

    estilo_subtit = ParagraphStyle('Subtit', fontName='Helvetica-Bold', fontSize=12, textColor=AZUL_HEADER, spaceAfter=10)
    elementos.append(Paragraph("RESUMEN CONTABLE", estilo_subtit))
    t_saldos = Table([
        [Paragraph("MEDIO", estilos['TH']), Paragraph("SISTEMA (ESPERADO)", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)), Paragraph("CAJERO (DECLARADO)", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)), Paragraph("DIFERENCIA", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT))],
        [Paragraph("Físico (Efectivo)", estilos['TD']), Paragraph(f"${esp_ef:,.2f}", estilos['TD_Right']), Paragraph(f"${real_ef:,.2f}", estilos['TD_Right']), Paragraph(f"${(real_ef - esp_ef):,.2f}", estilos['TD_Right'])],
        [Paragraph("Mercado Pago", estilos['TD']), Paragraph(f"${esp_mp:,.2f}", estilos['TD_Right']), Paragraph(f"${real_mp:,.2f}", estilos['TD_Right']), Paragraph(f"${(real_mp - esp_mp):,.2f}", estilos['TD_Right'])],
        [Paragraph("<b>TOTAL GENERAL</b>", estilos['TD']), Paragraph(f"<b>${total_esp:,.2f}</b>", estilos['TD_Right']), Paragraph(f"<b>${total_real:,.2f}</b>", estilos['TD_Right']), Paragraph(f"<b>${dif_total:,.2f}</b>", estilos['TD_Right'])],
    ], colWidths=[5 * cm, 4.5 * cm, 4.5 * cm, 5 * cm])
    t_saldos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0, 3), (-1, 3), 1, colors.HexColor('#94a3b8')),
    ]))
    elementos.append(t_saldos)

    if dif_total != 0:
        elementos.append(Spacer(1, 0.3 * cm))
        color_dif = colors.red if dif_total < 0 else colors.green
        elementos.append(Paragraph(
            f"DIFERENCIA TOTAL: ${dif_total:,.2f}",
            ParagraphStyle('Dif', fontName='Helvetica-Bold', textColor=color_dif),
        ))
        if sesion.observaciones:
            elementos.append(Paragraph(f"Justificación: {escapar(sesion.observaciones)}", estilos['DatosEmpresa']))

    elementos.append(Spacer(1, 0.8 * cm))
    elementos.append(Paragraph("DETALLE DE MOVIMIENTOS", estilo_subtit))
    rows = [[
        Paragraph("FECHA Y HORA", estilos['TH']),
        Paragraph("TIPO", estilos['TH']),
        Paragraph("CONCEPTO Y DESCRIPCIÓN", estilos['TH']),
        Paragraph("MÉTODO", estilos['TH']),
        Paragraph("MONTO", ParagraphStyle('THR', parent=estilos['TH'], alignment=TA_RIGHT)),
    ]]
    for mov in movimientos:
        signo = "+" if mov.tipo == "INGRESO" else "-"
        texto_concepto = f"<b>{escapar(mov.get_concepto_display())}</b>"
        if mov.descripcion:
            texto_concepto += f"<br/><font color='#64748b' size='7'>{escapar(mov.descripcion)}</font>"
        rows.append([
            Paragraph(formatear_fecha_operacion(mov.fecha, con_hora=True), estilos['TD']),
            Paragraph(escapar(mov.tipo), estilos['TD']),
            Paragraph(texto_concepto, estilos['TD']),
            Paragraph(escapar(mov.get_metodo_pago_display()), estilos['TD']),
            Paragraph(f"{signo}${mov.monto:,.2f}", estilos['TD_Right']),
        ])
    t_movs = Table(rows, colWidths=[3 * cm, 2.2 * cm, 7 * cm, 3 * cm, 3.8 * cm], repeatRows=1)
    t_movs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elementos.append(t_movs)
    elementos.append(Spacer(1, 2 * cm))

    t_firmas = Table([
        [Paragraph("________________________________", ParagraphStyle('Firma', alignment=TA_CENTER)), Paragraph("________________________________", ParagraphStyle('Firma', alignment=TA_CENTER))],
        [Paragraph(f"Firma Usuario caja: {escapar(usuario_cierre)}", ParagraphStyle('FirmaT', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9, textColor=GRIS_TEXTO)), Paragraph("Firma Administrador", ParagraphStyle('FirmaT', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9, textColor=GRIS_TEXTO))],
    ], colWidths=[9.5 * cm, 9.5 * cm])
    elementos.append(t_firmas)

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


# ====================================================================
#  7. BALANCE OPERATIVO (antes generado en Dashboard.vue)
# ====================================================================
def generar_balance_operativo_pdf(datos, config=None, datos_emision=None, filtros=None):
    datos = datos or {}
    datos_emision = datos_emision or obtener_datos_emision(None)
    config = obtener_configuracion(config)
    buffer = BytesIO()
    estilos = get_estilos()

    elementos = [
        construir_encabezado(config, 'BALANCE DE RENDIMIENTO', [
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
            ('PERÍODO', formatear_periodo_balance(filtros)),
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
        ], estilos),
        Spacer(1, 0.3 * cm),
        Paragraph('1. Resultados del Período', estilos['Seccion']),
    ]

    ingresos = float(datos.get('ingresosTotales') or 0)
    egresos = float(datos.get('egresosTotales') or 0)
    servicios = float(datos.get('serviciosRealizados') or 0)
    productos = float(datos.get('productosVendidos') or 0)
    operaciones = servicios + productos
    ticket = ingresos / operaciones if operaciones else 0

    def tarjeta(etiqueta, valor, color):
        estilo_valor = ParagraphStyle(f"Valor_{etiqueta}", fontName='Helvetica-Bold', fontSize=18,
                                      textColor=color, alignment=TA_CENTER)
        return [
            Paragraph(escapar(etiqueta.upper()), ParagraphStyle(f"Etq_{etiqueta}", fontName='Helvetica-Bold',
                                                               fontSize=9, textColor=GRIS_CLARO, alignment=TA_CENTER)),
            Spacer(1, 8),
            Paragraph(escapar(valor), estilo_valor),
        ]

    t_kpis = Table([[
        tarjeta('Ingresos', f"$ {_formato_numero(ingresos)}", VERDE_EXITO),
        tarjeta('Egresos', f"$ {_formato_numero(egresos)}", ROJO),
        tarjeta('Ticket Promedio', f"$ {_formato_numero(ticket)}", AZUL_CLARO),
        tarjeta('Operaciones', str(int(operaciones)), AZUL_HEADER),
    ]], colWidths=[4.25 * cm] * 4)
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), FONDO_ZEBRA),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#fffcfc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.extend([t_kpis, Spacer(1, 0.3 * cm)])

    elementos.append(Paragraph('2. Evolución de Ingresos', estilos['Seccion']))
    elementos.append(crear_grafico_lineas(
        datos.get('labelsDias') or [], datos.get('ventasPorDia') or [],
        ancho=17 * cm, alto=3.8 * cm,
    ))
    elementos.append(Spacer(1, 0.3 * cm))

    elementos.append(Paragraph('3. Análisis de Medios de Pago', estilos['Seccion']))
    medios = datos.get('ingresosPorMedio') or []
    if medios:
        paleta = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899']
        filas_medios = []
        for indice, medio in enumerate(medios):
            color = paleta[indice % len(paleta)]
            nombre = escapar(medio.get('medio') or '-')
            filas_medios.append([
                Paragraph(f'<font color="{color}">●</font> {nombre}', estilos['TD']),
                Paragraph(f"$ {_formato_numero(medio.get('total'))}", estilos['TD_Right']),
            ])
        t_medios = Table(filas_medios, colWidths=[12 * cm, 7 * cm])
        t_medios.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_medios)
    else:
        elementos.append(Paragraph('No se registraron cobros en el período.', estilos['TD']))

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


# ====================================================================
#  8. REPORTE ESTRATÉGICO (antes generado en EstadisticasDashboard.vue)
# ====================================================================
def generar_reporte_estrategico_pdf(datos, config=None, datos_emision=None,
                                    fecha_inicio=None, fecha_fin=None):
    datos = datos or {}
    datos_emision = datos_emision or obtener_datos_emision(None)
    config = obtener_configuracion(config)
    buffer = BytesIO()
    estilos = get_estilos()
    kpis = datos.get('kpis') or {}
    graficos = datos.get('graficos') or {}
    tablas = datos.get('tablas') or {}

    periodo = f"{formatear_fecha_filtro(fecha_inicio)} al {formatear_fecha_filtro(fecha_fin)}"
    elementos = [
        construir_encabezado(config, 'REPORTE ADMINISTRATIVO', [
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
            ('PERÍODO', periodo),
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
        ], estilos),
        Spacer(1, 0.8 * cm),
        Paragraph('1. Indicadores Clave', estilos['Seccion']),
    ]

    fidelidad = kpis.get('fidelidad') or {}
    servicio_estrella = kpis.get('servicio_estrella') or {}
    producto_estrella = kpis.get('producto_estrella') or {}
    indicadores = [
        ('Facturación Bruta', _formato_moneda(kpis.get('ingreso_total')),
         f"Ticket Prom: {_formato_moneda(kpis.get('ticket_promedio'))}"),
        ('Clientes Recurrentes', f"{fidelidad.get('tasa', 0)}%",
         f"Recurrentes: {fidelidad.get('recurrentes', 0)} | Nuevos: {fidelidad.get('nuevos', 0)}"),
        ('Ingreso de Operaciones', _formato_moneda(kpis.get('ingreso_operaciones')),
         'Ventas, turnos y pedidos web'),
        ('Ingreso por Cancelaciones', _formato_moneda(kpis.get('ingreso_penalizaciones')),
         'Señas retenidas'),
        ('Servicio Estrella', str(servicio_estrella.get('nombre') or 'Ninguno'),
         f"{servicio_estrella.get('cantidad', 0)} usos · {_formato_moneda(servicio_estrella.get('ingreso'))}"),
        ('Producto Estrella', str(producto_estrella.get('nombre') or 'Ninguno'),
         f"{producto_estrella.get('cantidad', 0)} unidades · {_formato_moneda(producto_estrella.get('ingreso'))}"),
    ]
    tarjetas = []
    for etiqueta, valor, detalle in indicadores:
        tarjetas.append([
            Paragraph(escapar(etiqueta.upper()), ParagraphStyle(f"Etq_{etiqueta}", fontName='Helvetica-Bold', fontSize=9, textColor=GRIS_CLARO)),
            Spacer(1, 4),
            Paragraph(escapar(valor), ParagraphStyle(f"Val_{etiqueta}", fontName='Helvetica-Bold', fontSize=14, textColor=AZUL_HEADER)),
            Spacer(1, 3),
            Paragraph(escapar(detalle), ParagraphStyle(f"Det_{etiqueta}", fontName='Helvetica', fontSize=8, textColor=GRIS_CLARO)),
        ])
    t_indicadores = Table([tarjetas[:2], tarjetas[2:4], tarjetas[4:6]], colWidths=[9.5 * cm, 9.5 * cm])
    t_indicadores.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.extend([t_indicadores, Spacer(1, 0.8 * cm)])

    turnos_ingresos = graficos.get('turnos_ingresos') or []
    ingresos_turnos = next((i.get('total', 0) for i in turnos_ingresos if i.get('label') == 'Turnos Completados'), 0)
    ingresos_senas = next((i.get('total', 0) for i in turnos_ingresos if i.get('label') == 'Señas Retenidas'), 0)
    elementos.append(Paragraph('2. Ingresos por Turnos', estilos['Seccion']))
    texto_turnos = [
        Paragraph(f"<b>Turnos Completados:</b> {_formato_moneda(ingresos_turnos)}", estilos['TD']),
        Paragraph(f"<b>Señas Retenidas:</b> {_formato_moneda(ingresos_senas)}", estilos['TD']),
        Spacer(1, 5),
        Paragraph(f"<b>TOTAL INGRESOS POR TURNOS: {_formato_moneda(ingresos_turnos + ingresos_senas)}</b>",
                  ParagraphStyle('TotalTurnos', fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_HEADER)),
    ]
    t_turnos = Table([[
        crear_grafico_dona(turnos_ingresos, texto_centro=formato_moneda_compacta_arg(ingresos_turnos + ingresos_senas)),
        texto_turnos,
    ]], colWidths=[6 * cm, 13 * cm])
    t_turnos.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elementos.extend([t_turnos, Spacer(1, 0.8 * cm)])

    medios_pago = graficos.get('medios_pago') or []
    total_medios = sum(float(m.get('total') or 0) for m in medios_pago)
    elementos.append(Paragraph('3. Medios de Pago', estilos['Seccion']))
    texto_medios = [
        Paragraph(f"<b>{escapar(m.get('medio'))}:</b> {_formato_moneda(m.get('total'))}", estilos['TD'])
        for m in medios_pago
    ] or [Paragraph('Sin datos.', estilos['TD'])]
    texto_medios += [
        Spacer(1, 5),
        Paragraph(f"<b>TOTAL PAGOS: {_formato_moneda(total_medios)}</b>",
                  ParagraphStyle('TotalPagos', fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_HEADER)),
    ]
    t_medios = Table([[
        crear_grafico_dona([
            {'total': m.get('total'), 'color': ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'][i % 5]}
            for i, m in enumerate(medios_pago)
        ], texto_centro=formato_moneda_compacta_arg(total_medios)),
        texto_medios,
    ]], colWidths=[6 * cm, 13 * cm])
    t_medios.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elementos.extend([t_medios, Spacer(1, 0.8 * cm)])

    servicios = graficos.get('servicios_mas_elegidos') or []
    productos = graficos.get('productos_mas_vendidos') or []
    if servicios or productos:
        def bloque_ranking(titulo, items, unidad):
            lineas = []
            for item in items:
                cantidad = int(item.get('cantidad') or 0)
                etiqueta = unidad if cantidad == 1 else unidad + 's'
                lineas.append(Paragraph(
                    f"<b>{escapar(item.get('nombre'))}:</b> {cantidad} {etiqueta} · {_formato_moneda(item.get('ingreso'))}",
                    estilos['TD'],
                ))
            if not lineas:
                lineas = [Paragraph('Sin datos.', estilos['TD'])]
            return [
                Paragraph(titulo, estilos['Subtitulo']),
                crear_grafico_barras(items, ancho=8 * cm, alto=5.5 * cm),
                *lineas,
            ]

        t_rankings = Table([[
            bloque_ranking('4. Servicios Más Elegidos', servicios, 'uso'),
            bloque_ranking('5. Productos Más Vendidos', productos, 'unidad'),
        ]], colWidths=[9.5 * cm, 9.5 * cm])
        t_rankings.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elementos.extend([t_rankings, Spacer(1, 0.8 * cm)])

    elementos.append(Paragraph('6. Stock Estancado (Top 5)', estilos['Seccion']))
    filas_stock = [[Paragraph(x, estilos['TH']) for x in ('PRODUCTO', 'MARCA', 'STOCK', 'CAPITAL PARADO')]]
    for item in tablas.get('stock_estancado') or []:
        filas_stock.append([
            Paragraph(escapar(item.get('producto')), estilos['TD']),
            Paragraph(escapar(item.get('marca') or 'Sin Marca'), estilos['TD']),
            Paragraph(str(item.get('stock', 0)), ParagraphStyle('StockC', parent=estilos['TD'], alignment=TA_CENTER, fontName='Helvetica-Bold')),
            Paragraph(_formato_moneda(item.get('capital')), ParagraphStyle('Capital', parent=estilos['TD_Right'], fontName='Helvetica-Bold', textColor=ROJO)),
        ])
    if len(filas_stock) == 1:
        filas_stock.append([Paragraph('Excelente rotación. Todos los productos se movieron.', estilos['TD'])] + [Paragraph('', estilos['TD'])] * 3)
    elementos.append(crear_tabla_datos(filas_stock, [6 * cm, 4 * cm, 3 * cm, 6 * cm], estilos))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph('7. Señas Retenidas (Cancelaciones)', estilos['Seccion']))
    filas_senas = [[Paragraph(x, estilos['TH']) for x in ('FECHA', 'CLIENTE', 'SERVICIO', 'MONTO')]]
    for item in tablas.get('penalizaciones') or []:
        filas_senas.append([
            Paragraph(escapar(formatear_fecha_operacion(item.get('fecha'), con_hora=False)), estilos['TD']),
            Paragraph(escapar(item.get('cliente')), estilos['TD']),
            Paragraph(escapar(item.get('servicio')), estilos['TD']),
            Paragraph(f"+ {_formato_moneda(item.get('monto_retenido'))}", ParagraphStyle('Senna', parent=estilos['TD_Right'], fontName='Helvetica-Bold', textColor=VERDE_EXITO)),
        ])
    if len(filas_senas) == 1:
        filas_senas.append([Paragraph('No hubo cancelaciones con retención de seña en este período.', estilos['TD'])] + [Paragraph('', estilos['TD'])] * 3)
    elementos.append(crear_tabla_datos(filas_senas, [3 * cm, 5 * cm, 7 * cm, 4 * cm], estilos))

    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()


def generar_pdf_error(mensaje, config=None, datos_emision=None, titulo='ERROR AL GENERAR REPORTE'):
    """PDF de error con encabezado, pie y trazabilidad institucionales."""
    return _generar_pdf_error_institucional(mensaje, config, datos_emision, titulo)
