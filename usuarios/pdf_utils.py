# usuarios/pdf_utils.py
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from django.http import HttpResponse
from django.conf import settings
import os

def generar_comprobante_venta(venta, detalles):
    """
    Genera un comprobante PDF profesional para una venta
    """
    try:
        print(f"🔍 PDF_UTILS: Generando PDF profesional para venta {venta.id}")
        
        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Crear documento con márgenes optimizados
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Estilos profesionales
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            alignment=1,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold'
        )
        
        # Estilo para información
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica'
        )
        
        # Elementos del documento
        elements = []
        
        # ✅ ENCABEZADO PROFESIONAL CON LOGO
        header_data = [
            [Paragraph("<b>HAIRSOFT</b>", title_style)],
            [Paragraph("PELUQUERÍA & ESTÉTICA", subtitle_style)],
            [Paragraph("COMPROBANTE DE VENTA", subtitle_style)],
        ]
        
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 15))
        
        # ✅ INFORMACIÓN DE LA VENTA MEJORADA
        cliente_nombre = "Cliente General"
        vendedor_nombre = "Sistema"
        
        if venta.cliente:
            cliente_nombre = f"{getattr(venta.cliente, 'nombre', '')} {getattr(venta.cliente, 'apellido', '')}".strip()
        
        if venta.usuario:
            vendedor_nombre = f"{getattr(venta.usuario, 'nombre', '')} {getattr(venta.usuario, 'apellido', '')}".strip()
        
        info_data = [
            [Paragraph('<b><font color="#2c3e50">N° COMPROBANTE:</font></b>', info_style), 
             Paragraph(f'<font color="#e74c3c"><b>#{venta.id}</b></font>', info_style)],
            
            [Paragraph('<b><font color="#2c3e50">FECHA Y HORA:</font></b>', info_style), 
             Paragraph(f'{venta.fecha.strftime("%d/%m/%Y %H:%M")}', info_style)],
            
            [Paragraph('<b><font color="#2c3e50">CLIENTE:</font></b>', info_style), 
             Paragraph(cliente_nombre, info_style)],
            
            [Paragraph('<b><font color="#2c3e50">VENDEDOR:</font></b>', info_style), 
             Paragraph(vendedor_nombre, info_style)],
            
            [Paragraph('<b><font color="#2c3e50">MÉTODO DE PAGO:</font></b>', info_style), 
             Paragraph(f'<font color="#27ae60">{getattr(venta.medio_pago, "nombre", "Efectivo")}</font>', info_style)],
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # ✅ TABLA DE PRODUCTOS MEJORADA
        elements.append(Paragraph("DETALLE DE PRODUCTOS", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Encabezados de la tabla
        product_data = [
            ['PRODUCTO', 'CANTIDAD', 'P. UNITARIO', 'SUBTOTAL']
        ]
        
        # Agregar productos
        total_venta = 0
        for detalle in detalles:
            if hasattr(detalle, 'producto') and detalle.producto:
                producto_nombre = getattr(detalle.producto, 'nombre', 'Producto')
                cantidad = getattr(detalle, 'cantidad', 0)
                precio_unitario = getattr(detalle, 'precio_unitario', 0)
                subtotal = getattr(detalle, 'subtotal', 0)
                
                total_venta += subtotal
                
                product_data.append([
                    producto_nombre, 
                    str(cantidad), 
                    f"${precio_unitario:.2f}", 
                    f"${subtotal:.2f}"
                ])
        
        # Si no hay productos, mostrar mensaje
        if len(product_data) == 1:
            product_data.append(['No hay productos registrados', '', '', ''])
        
        # Crear tabla de productos
        product_table = Table(product_data, colWidths=[3.2*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        product_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Filas de datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7f8c8d')),
        ]))
        
        elements.append(product_table)
        elements.append(Spacer(1, 20))
        
        # ✅ TOTAL DESTACADO
        total_data = [
            ['', '', Paragraph('<b><font size="12">TOTAL:</font></b>', info_style), 
             Paragraph(f'<font size="12" color="#e74c3c"><b>${total_venta:.2f}</b></font>', info_style)]
        ]
        
        total_table = Table(total_data, colWidths=[3.2*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(total_table)
        elements.append(Spacer(1, 30))
        
        # ✅ PIE DE PÁGINA PROFESIONAL
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=1,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica-Oblique'
        )
        
        elements.append(Paragraph("¡Gracias por su preferencia!", footer_style))
        elements.append(Paragraph("HairSoft - Sistema de Gestión Profesional", footer_style))
        elements.append(Paragraph("Tel: (123) 456-7890 | Email: info@hairsoft.com", footer_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Este comprobante es generado automáticamente por el sistema", 
                                ParagraphStyle('Small', parent=footer_style, fontSize=8)))
        
        # Generar PDF
        doc.build(elements)
        
        # Obtener el PDF del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF_UTILS: PDF profesional generado exitosamente para venta {venta.id}")
        return pdf
        
    except Exception as e:
        print(f"❌ PDF_UTILS: Error generando PDF: {str(e)}")
        import traceback
        print(f"❌ PDF_UTILS: Traceback: {traceback.format_exc()}")
        return None