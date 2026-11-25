"""
Helpers institucionales compartidos por todos los PDF de HairSoft.

Toda la información de la empresa se toma de ConfiguracionSistema.get_solo().
No existen valores fijos de empresa ni logos de reserva: si un dato no está
configurado, simplemente no se imprime.
"""
from datetime import date, datetime, time
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape

import requests
from django.utils import timezone
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfgen_canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import ConfiguracionSistema

# --- Estilos/colores institucionales -------------------------------------------------
AZUL_HEADER = colors.HexColor('#0f172a')
GRIS_TEXTO = colors.HexColor('#334155')
GRIS_CLARO = colors.HexColor('#64748b')
FONDO_ZEBRA = colors.HexColor('#f8fafc')
BLANCO = colors.HexColor('#ffffff')
VERDE_EXITO = colors.HexColor('#10b981')
ROJO = colors.HexColor('#ef4444')
AZUL_CLARO = colors.HexColor('#0ea5e9')
NARANJA = colors.HexColor('#f59e0b')

PIE_INSTITUCIONAL = "HairSoft - Sistema de Gestión Integral"
GENERACION_AUTOMATICA = "Generación automática"
SOLICITANTE_NO_VERIFICADO = "Solicitante no verificado"
ROLES_ADMINISTRATIVOS_PDF = {'ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'RECEPCIÓN', 'RECEPCION'}

FORMATO_FECHA = '%d/%m/%Y'
FORMATO_FECHA_HORA = '%d/%m/%Y %H:%M'
FORMATO_FECHA_HORA_SEGUNDOS = '%d/%m/%Y %H:%M:%S'


def get_estilos():
    """Estilos base compartidos por todos los documentos."""
    styles = getSampleStyleSheet()
    return {
        'Empresa': ParagraphStyle(
            'Empresa', parent=styles['Normal'], fontName='Helvetica-Bold',
            fontSize=11, textColor=AZUL_HEADER, textTransform='uppercase', leading=13,
        ),
        'DatosEmpresa': ParagraphStyle(
            'DatosEmpresa', parent=styles['Normal'], fontName='Helvetica',
            fontSize=10, textColor=GRIS_TEXTO, leading=12,
        ),
        'TituloDer': ParagraphStyle(
            'TituloDer', parent=styles['Normal'], fontName='Helvetica-Bold',
            fontSize=14, textColor=AZUL_HEADER, alignment=TA_RIGHT,
            textTransform='uppercase', spaceAfter=5,
        ),
        'DatoDerL': ParagraphStyle(
            'DatoDerL', parent=styles['Normal'], fontName='Helvetica',
            fontSize=9, textColor=GRIS_CLARO, alignment=TA_RIGHT,
            textTransform='uppercase',
        ),
        'DatoDerV': ParagraphStyle(
            'DatoDerV', parent=styles['Normal'], fontName='Helvetica-Bold',
            fontSize=10, textColor=AZUL_HEADER, alignment=TA_RIGHT,
        ),
        'TH': ParagraphStyle(
            'TH', fontName='Helvetica-Bold', fontSize=9, textColor=BLANCO,
        ),
        'TD': ParagraphStyle(
            'TD', fontName='Helvetica', fontSize=9, textColor=GRIS_TEXTO, leading=11,
        ),
        'TD_Right': ParagraphStyle(
            'TD_Right', parent=styles['Normal'], fontName='Helvetica',
            fontSize=9, textColor=GRIS_TEXTO, alignment=TA_RIGHT, leading=11,
        ),
        'Subtitulo': ParagraphStyle(
            'Subtitulo', fontName='Helvetica-Bold', fontSize=12,
            textColor=AZUL_HEADER, spaceAfter=10,
        ),
        'Seccion': ParagraphStyle(
            'Seccion', fontName='Helvetica-Bold', fontSize=13,
            textColor=AZUL_HEADER, spaceBefore=6, spaceAfter=10,
        ),
        'Pie': ParagraphStyle(
            'Pie', fontName='Helvetica', fontSize=8, textColor=GRIS_CLARO,
        ),
    }


def escapar(valor):
    """Escapa texto para Paragraph sin alterar el contenido institucional."""
    if valor is None:
        return ''
    return xml_escape(str(valor))


def obtener_configuracion(config=None):
    """Devuelve la configuración institucional existente; nunca crea otra fuente."""
    if config is not None:
        return config
    try:
        return ConfiguracionSistema.get_solo()
    except Exception:
        return None


def datos_institucionales(config=None):
    config = obtener_configuracion(config)
    if config is None:
        return {
            'razon_social': '', 'cuil_cuit': '', 'direccion': '',
            'telefono': '', 'email': '', 'logo': None,
        }
    return {
        'razon_social': getattr(config, 'razon_social', '') or '',
        'cuil_cuit': getattr(config, 'cuil_cuit', '') or '',
        'direccion': getattr(config, 'direccion', '') or '',
        'telefono': getattr(config, 'telefono', '') or '',
        'email': getattr(config, 'email', '') or '',
        'logo': getattr(config, 'logo', None),
    }


def obtener_logo_reporte(config=None):
    """Devuelve únicamente el logo configurado. Si no hay logo, no se dibuja nada."""
    config = obtener_configuracion(config)
    if config is None:
        return None
    logo = getattr(config, 'logo', None)
    if not logo:
        return None

    # Primero se intenta el archivo local (evita una request innecesaria).
    try:
        ruta = logo.path
        if ruta:
            return Image(ruta, width=2.2 * cm, height=2.2 * cm)
    except Exception:
        pass

    # En almacenamiento remoto (por ejemplo Cloudinary) se usa la URL configurada.
    try:
        respuesta = requests.get(logo.url, timeout=5)
        if respuesta.status_code == 200:
            return Image(BytesIO(respuesta.content), width=2.2 * cm, height=2.2 * cm)
    except Exception as exc:
        print(f"No se pudo cargar el logo configurado: {exc}")
    return None


def nombre_usuario(usuario):
    """Nombre del usuario real autenticado, reutilizando el helper de auditoría."""
    if usuario is None:
        return ''
    try:
        from .auditoria_service import _nombre_completo
        return _nombre_completo(usuario) or ''
    except Exception:
        nombre = f"{getattr(usuario, 'nombre', '')} {getattr(usuario, 'apellido', '')}".strip()
        return nombre or getattr(usuario, 'correo', '') or str(usuario)


def normalizar_rol(usuario):
    """Rol del usuario normalizado, sin inferir roles desde datos del frontend."""
    if usuario is None:
        return ''
    if getattr(usuario, 'is_superuser', False) or getattr(usuario, 'is_staff', False):
        return 'ADMINISTRADOR'
    rol = getattr(usuario, 'rol', None)
    if rol is None:
        return ''
    return str(getattr(rol, 'nombre', '') or '').strip().upper()


def es_admin_o_recepcion(usuario):
    """Administración/Recepción según rol persistido o flags de Django."""
    if usuario is None:
        return False
    if getattr(usuario, 'is_superuser', False) or getattr(usuario, 'is_staff', False):
        return True
    return normalizar_rol(usuario) in ROLES_ADMINISTRATIVOS_PDF


def puede_descargar_comprobante(usuario, titular_id):
    """
    Autoriza la descarga de un comprobante por titularidad o rol administrativo.

    La identidad y el rol se toman de request.user; nunca de parámetros ni headers
    enviados por el frontend.
    """
    if usuario is None or not getattr(usuario, 'is_authenticated', False):
        return False
    if es_admin_o_recepcion(usuario):
        return True
    return titular_id is not None and getattr(usuario, 'id', None) == titular_id


def obtener_datos_emision(request=None, incluir_usuario=True, automatico=False):
    """
    Registra una única vez la fecha/hora real de emisión y al solicitante.

    - Solicitud HTTP autenticada: nombre real del usuario de request.user.
    - Solicitud HTTP sin identidad verificable: 'Solicitante no verificado'.
    - Proceso automático del sistema: 'Generación automática'.

    Se conserva la clave 'usuario' por compatibilidad con generadores existentes.
    """
    fecha_emision = timezone.localtime(timezone.now()).strftime(FORMATO_FECHA_HORA_SEGUNDOS)

    if automatico or request is None:
        solicitante = GENERACION_AUTOMATICA
        return {
            'fecha_emision': fecha_emision,
            'usuario': solicitante,
            'solicitante': solicitante,
            'origen': 'SISTEMA',
            'rol': '',
        }

    usuario_autenticado = getattr(request, 'user', None)
    if incluir_usuario and getattr(usuario_autenticado, 'is_authenticated', False):
        solicitante = nombre_usuario(usuario_autenticado) or SOLICITANTE_NO_VERIFICADO
        origen = 'AUTENTICADO'
        rol = normalizar_rol(usuario_autenticado)
    else:
        solicitante = SOLICITANTE_NO_VERIFICADO
        origen = 'ANONIMO'
        rol = ''

    return {
        'fecha_emision': fecha_emision,
        'usuario': solicitante,
        'solicitante': solicitante,
        'origen': origen,
        'rol': rol,
    }


def solicitante_emision(datos_emision):
    """Nombre del solicitante, compatible con diccionarios de emisión anteriores."""
    datos = datos_emision or obtener_datos_emision(None)
    return datos.get('solicitante') or datos.get('usuario') or SOLICITANTE_NO_VERIFICADO


def formatear_fecha_operacion(valor, con_hora=True):
    """Formatea fechas de operación respetando America/Argentina/Buenos_Aires."""
    if valor in (None, ''):
        return '-'
    formato = FORMATO_FECHA_HORA if con_hora else FORMATO_FECHA
    if isinstance(valor, datetime):
        if timezone.is_aware(valor):
            valor = timezone.localtime(valor)
        return valor.strftime(formato)
    if isinstance(valor, date):
        return valor.strftime(FORMATO_FECHA)
    if isinstance(valor, time):
        return valor.strftime('%H:%M')
    if isinstance(valor, str):
        texto = valor.strip()
        try:
            fecha = datetime.fromisoformat(texto.replace('Z', '+00:00'))
            if timezone.is_aware(fecha):
                fecha = timezone.localtime(fecha)
            return fecha.strftime(formato)
        except (ValueError, TypeError):
            try:
                return datetime.strptime(texto, '%Y-%m-%d').strftime(FORMATO_FECHA)
            except (ValueError, TypeError):
                return texto
    return str(valor)


def formatear_fecha_filtro(valor):
    return formatear_fecha_operacion(valor, con_hora=False)


def bloque_derecho(titulo, pares, estilos=None):
    """Bloque derecho estándar: título, etiqueta y valor para cada dato."""
    estilos = estilos or get_estilos()
    bloque = [Paragraph(escapar(titulo), estilos['TituloDer']), Spacer(1, 6)]
    for etiqueta, valor in pares:
        bloque.extend([
            Paragraph(escapar(etiqueta), estilos['DatoDerL']),
            Paragraph(escapar(valor) if valor not in (None, '') else '-', estilos['DatoDerV']),
            Spacer(1, 3),
        ])
    return bloque


def construir_encabezado(config, titulo, pares, estilos=None, incluir_logo=True):
    """Encabezado institucional común, con los datos parametrizables de la empresa."""
    estilos = estilos or get_estilos()
    datos = datos_institucionales(config)
    izquierda = []
    if datos['razon_social']:
        izquierda.extend([
            Paragraph(escapar(datos['razon_social']), estilos['Empresa']),
            Spacer(1, 4),
        ])
    for etiqueta, clave in (
        ('CUIT', 'cuil_cuit'),
        ('DIRECCIÓN', 'direccion'),
        ('TELÉFONO', 'telefono'),
        ('EMAIL', 'email'),
    ):
        if datos[clave]:
            izquierda.append(
                Paragraph(f"<b>{escapar(etiqueta)}:</b> {escapar(datos[clave])}", estilos['DatosEmpresa'])
            )
    if not izquierda:
        izquierda = [Paragraph('', estilos['DatosEmpresa'])]

    logo = obtener_logo_reporte(config) if incluir_logo else None
    if logo:
        bloque_izquierdo = Table([[logo, izquierda]], colWidths=[2.5 * cm, 9.5 * cm])
        bloque_izquierdo.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
    else:
        bloque_izquierdo = izquierda

    tabla = Table(
        [[bloque_izquierdo, bloque_derecho(titulo, pares, estilos)]],
        colWidths=[12 * cm, 7 * cm],
    )
    tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, 0), (-1, -1), 2, AZUL_HEADER),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    return tabla


class NumeroPaginasCanvas(pdfgen_canvas.Canvas):
    """Canvas que dibuja el pie con el total real de páginas al cerrar el PDF."""

    def __init__(self, *args, sello_liquidado=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._estados_pagina = []
        self._sello_liquidado = sello_liquidado

    def showPage(self):
        self._estados_pagina.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_paginas = len(self._estados_pagina)
        for estado in self._estados_pagina:
            self.__dict__.update(estado)
            self._dibujar_pie(total_paginas)
            if self._sello_liquidado:
                self._dibujar_sello_liquidado(self._sello_liquidado)
            pdfgen_canvas.Canvas.showPage(self)
        super().save()

    def _dibujar_pie(self, total_paginas):
        ancho, _ = A4
        self.saveState()
        self.setFont('Helvetica', 8)
        self.setFillColor(GRIS_CLARO)
        self.drawCentredString(ancho / 2, 1.5 * cm, PIE_INSTITUCIONAL)
        self.drawRightString(
            ancho - 2 * cm, 1.5 * cm,
            f"Página {self.getPageNumber()} de {total_paginas}",
        )
        self.restoreState()

    def _dibujar_sello_liquidado(self, fecha_liquidacion):
        self.saveState()
        self.translate(300, 400)
        self.rotate(25)
        color_rojo = colors.Color(0.8, 0, 0, alpha=0.3)
        self.setStrokeColor(color_rojo)
        self.setFillColor(color_rojo)
        self.setLineWidth(5)
        self.roundRect(-100, -40, 200, 80, 10, stroke=1, fill=0)
        self.setFont('Helvetica-Bold', 40)
        self.drawCentredString(0, -10, 'PAGADO')
        self.setFont('Helvetica-Bold', 10)
        self.drawCentredString(0, -30, f"LIQUIDADO: {fecha_liquidacion}")
        self.restoreState()


def crear_documento(buffer):
    return SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=50,
    )


def construir_documento(doc, elementos, sello_liquidado=None):
    """Construye el PDF usando el pie institucional con numeración X de Y."""
    def canvasmaker(*args, **kwargs):
        return NumeroPaginasCanvas(*args, sello_liquidado=sello_liquidado, **kwargs)

    doc.build(elementos, canvasmaker=canvasmaker)


def dibujar_pie(canvas_obj, doc, total_paginas=1):
    """Compatible con el antiguo onPage; mantiene el pie institucional común."""
    NumeroPaginasCanvas._dibujar_pie(canvas_obj, total_paginas)


def sello_pagado(canvas_obj, doc, fecha_liquidacion=None):
    """Compatible con el antiguo onPage; usa la fecha de emisión capturada."""
    NumeroPaginasCanvas._dibujar_pie(canvas_obj, 1)
    if fecha_liquidacion:
        NumeroPaginasCanvas._dibujar_sello_liquidado(canvas_obj, fecha_liquidacion)


def formato_numero_arg(valor, decimales=3, conservar_decimales=False):
    """Formato es-AR equivalente a Intl.NumberFormat('es-AR') del frontend."""
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    texto = f"{numero:,.{decimales}f}"
    if decimales and not conservar_decimales:
        texto = texto.rstrip('0').rstrip('.')
    return texto.replace(',', '\u0001').replace('.', ',').replace('\u0001', '.')


def formato_moneda_arg(valor, decimales=2, con_espacio=True):
    prefijo = '$ ' if con_espacio else '$'
    return f"{prefijo}{formato_numero_arg(valor, decimales, conservar_decimales=True)}"


def formato_moneda_compacta_arg(valor):
    """Equivalente a formatCurrencyCompact del frontend."""
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    if abs(numero) >= 1000:
        return f"$ {formato_numero_arg(round(numero), 0)}"
    return formato_numero_arg(numero, 2, conservar_decimales=True)


def crear_grafico_lineas(labels, valores, ancho=17 * cm, alto=6.5 * cm):
    """Curva de ingresos por día, equivalente al gráfico SVG del dashboard."""
    dibujo = Drawing(ancho, alto)
    grafico = HorizontalLineChart()
    grafico.x = 40
    grafico.y = 35
    grafico.width = ancho - 55
    grafico.height = alto - 70
    datos = [float(v or 0) for v in (valores or [])]
    grafico.data = [datos] if datos else [[0]]
    grafico.categoryAxis.categoryNames = [str(x) for x in (labels or [])] or ['']
    grafico.categoryAxis.labels.fontSize = 7
    grafico.categoryAxis.labels.fillColor = GRIS_CLARO
    grafico.categoryAxis.labels.dy = -6
    grafico.categoryAxis.labels.angle = 45 if len(datos) > 8 else 0
    grafico.valueAxis.valueMin = 0
    grafico.valueAxis.valueMax = max(datos + [100]) * 1.1
    grafico.valueAxis.labels.fontSize = 7
    grafico.valueAxis.labels.fillColor = GRIS_CLARO
    grafico.lines[0].strokeColor = ROJO
    grafico.lines[0].strokeWidth = 2
    dibujo.add(grafico)
    return dibujo


def crear_grafico_dona(items, ancho=6 * cm, alto=6 * cm, texto_centro=''):
    """Dona con el mismo significado/color de los gráficos del frontend."""
    dibujo = Drawing(ancho, alto)
    if not items:
        dibujo.add(String(ancho / 2, alto / 2, 'Sin datos', textAnchor='middle',
                          fontName='Helvetica', fontSize=9, fillColor=GRIS_CLARO))
        return dibujo
    grafico = Pie()
    grafico.x = ancho / 2 - min(ancho, alto) / 2
    grafico.y = alto / 2 - min(ancho, alto) / 2
    grafico.width = min(ancho, alto)
    grafico.height = min(ancho, alto)
    grafico.data = [float(item.get('total') or 0) for item in items]
    grafico.slices.strokeWidth = 0.5
    grafico.slices.strokeColor = BLANCO
    for indice, item in enumerate(items):
        color = item.get('color') or ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'][indice % 5]
        grafico.slices[indice].fillColor = colors.HexColor(color)
    dibujo.add(grafico)
    if texto_centro:
        dibujo.add(String(ancho / 2, alto / 2 + 4, texto_centro, textAnchor='middle',
                          fontName='Helvetica-Bold', fontSize=9, fillColor=AZUL_HEADER))
        dibujo.add(String(ancho / 2, alto / 2 - 10, 'TOTAL', textAnchor='middle',
                          fontName='Helvetica-Bold', fontSize=7, fillColor=GRIS_CLARO))
    return dibujo


def crear_grafico_barras(items, ancho=8 * cm, alto=5.5 * cm):
    """Barras horizontales de ranking con la paleta del frontend."""
    dibujo = Drawing(ancho, alto)
    if not items:
        dibujo.add(String(ancho / 2, alto / 2, 'Sin datos', textAnchor='middle',
                          fontName='Helvetica', fontSize=9, fillColor=GRIS_CLARO))
        return dibujo
    grafico = HorizontalBarChart()
    grafico.x = 75
    grafico.y = 20
    grafico.width = ancho - 90
    grafico.height = alto - 40
    grafico.data = [[float(item.get('cantidad') or 0) for item in items]]
    grafico.categoryAxis.categoryNames = [str(item.get('nombre') or '') for item in items]
    grafico.categoryAxis.labels.fontSize = 7
    grafico.categoryAxis.labels.fillColor = GRIS_TEXTO
    grafico.valueAxis.valueMin = 0
    grafico.valueAxis.labels.fontSize = 7
    grafico.valueAxis.labels.fillColor = GRIS_CLARO
    grafico.barSpacing = 2
    grafico.groupSpacing = 4
    for indice, _ in enumerate(items):
        color = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'][indice % 5]
        grafico.bars[(0, indice)].fillColor = colors.HexColor(color)
    dibujo.add(grafico)
    return dibujo


def crear_tabla_datos(filas, col_widths, estilos=None, cabecera=True):
    """Tabla simple con el estilo institucional de las tablas de los reportes."""
    estilos = estilos or get_estilos()
    datos = []
    for fila in filas:
        estilo = estilos['TH'] if cabecera else estilos['TD']
        datos.append([celda if hasattr(celda, 'wrap') else Paragraph(escapar(celda), estilo) for celda in fila])
    tabla = Table(datos, colWidths=col_widths, repeatRows=1 if cabecera else 0)
    estilo_tabla = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]
    if cabecera:
        estilo_tabla.append(('BACKGROUND', (0, 0), (-1, 0), AZUL_HEADER))
    else:
        estilo_tabla.append(('BACKGROUND', (0, 0), (-1, -1), FONDO_ZEBRA))
    tabla.setStyle(TableStyle(estilo_tabla))
    return tabla


def generar_pdf_error(mensaje, config=None, datos_emision=None, titulo='ERROR AL GENERAR REPORTE'):
    """PDF de error con el mismo encabezado, pie y trazabilidad que los demás."""
    buffer = BytesIO()
    estilos = get_estilos()
    datos_emision = datos_emision or obtener_datos_emision(None)
    elementos = [
        construir_encabezado(config, titulo, [
            ('FECHA EMISIÓN', datos_emision['fecha_emision']),
            ('SOLICITADO POR', solicitante_emision(datos_emision)),
        ], estilos),
        Spacer(1, 1 * cm),
        Paragraph(escapar(mensaje).replace('\n', '<br/>'), estilos['TD']),
    ]
    construir_documento(crear_documento(buffer), elementos)
    return buffer.getvalue()
