# app/pdf_generator.py
"""
Especially API — Generador de PDF de especificaciones para producción.

Usa ReportLab para construir el documento en memoria y devolverlo como bytes
listos para subir a R2. El PDF incluye datos del pedido, detalle de ítems,
tallas, colores e imágenes de los diseños personalizados.

Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
"""
import io
import urllib.request
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .models import Order


# ─── Paleta de colores Especially ─────────────────────────────────────────────
PRIMARY   = colors.HexColor("#1A1A2E")   # Azul oscuro
ACCENT    = colors.HexColor("#E94560")   # Rojo/coral
LIGHT_BG  = colors.HexColor("#F5F5F5")
GRAY      = colors.HexColor("#6B6B6B")
WHITE     = colors.white


def _fetch_image_bytes(url: str) -> Optional[bytes]:
    """Descarga una imagen desde una URL y devuelve los bytes. None si falla."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EspeciallyBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


def generate_spec_pdf(order: Order) -> bytes:
    """
    Genera el PDF de especificaciones para una orden.
    Devuelve el PDF como bytes listo para subir a R2.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Especificaciones - Pedido {str(order.order_id)[:8].upper()}",
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        "EspecTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=PRIMARY,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "EspecSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=GRAY,
        spaceAfter=12,
        fontName="Helvetica",
    )
    section_style = ParagraphStyle(
        "EspecSection",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        borderPad=0,
    )
    body_style = ParagraphStyle(
        "EspecBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        fontName="Helvetica",
        leading=14,
    )

    story = []

    # ── Encabezado ────────────────────────────────────────────────────────────
    story.append(Paragraph("especially", title_style))
    story.append(Paragraph("Hoja de Especificaciones para Producción", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=12))

    # ── Datos del pedido ──────────────────────────────────────────────────────
    order_id_short = str(order.order_id)[:8].upper()
    created_str = (
        order.created_at.strftime("%d/%m/%Y %H:%M")
        if order.created_at
        else datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    story.append(Paragraph("Información del Pedido", section_style))

    order_data = [
        ["ID de Pedido",     f"ESP-{order_id_short}"],
        ["Fecha de Creación", created_str],
        ["Tipo de Entrega",  order.shipping_type.value.capitalize() if order.shipping_type else "Normal"],
        ["Dirección de Entrega", order.shipping_address],
        ["Total",            f"${order.total_amount:,.0f} COP"],
    ]

    order_table = Table(order_data, colWidths=[5 * cm, 12 * cm])
    order_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR",   (0, 0), (0, -1), PRIMARY),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    story.append(order_table)

    # ── Items del pedido ──────────────────────────────────────────────────────
    story.append(Paragraph("Detalle de Productos", section_style))

    for idx, item in enumerate(order.items, start=1):
        product_name = item.product.name if item.product else "Producto no disponible"

        story.append(Paragraph(f"Ítem #{idx}: {product_name}", ParagraphStyle(
            "ItemTitle",
            parent=body_style,
            fontSize=11,
            textColor=ACCENT,
            fontName="Helvetica-Bold",
            spaceBefore=8,
            spaceAfter=4,
        )))

        item_data = [
            ["Producto",        product_name],
            ["Cantidad",        str(item.quantity)],
            ["Precio Unitario", f"${item.unit_price:,.0f} COP"],
            ["Talla",           item.size or "No especificada"],
            ["Color de Prenda", item.garment_color or "No especificado"],
        ]

        item_table = Table(item_data, colWidths=[5 * cm, 12 * cm])
        item_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (0, -1), LIGHT_BG),
            ("TEXTCOLOR",   (0, 0), (0, -1), PRIMARY),
            ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",(0, 0), (-1, -1), 8),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ]))
        story.append(item_table)

        # Imagen del diseño personalizado
        if item.design and item.design.preview_image_url:
            story.append(Spacer(1, 0.4 * cm))
            story.append(Paragraph("Diseño Personalizado:", ParagraphStyle(
                "DesignLabel",
                parent=body_style,
                fontName="Helvetica-Bold",
                textColor=PRIMARY,
                spaceAfter=4,
            )))

            img_bytes = _fetch_image_bytes(item.design.preview_image_url)
            if img_bytes:
                img_buffer = io.BytesIO(img_bytes)
                try:
                    design_img = Image(img_buffer, width=8 * cm, height=8 * cm)
                    design_img.hAlign = "LEFT"
                    story.append(design_img)
                except Exception:
                    story.append(Paragraph(
                        f"[Imagen no disponible: {item.design.preview_image_url}]",
                        body_style,
                    ))
            else:
                story.append(Paragraph(
                    f"URL del diseño: {item.design.preview_image_url}",
                    body_style,
                ))

        story.append(Spacer(1, 0.3 * cm))

    # ── Pie de página ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BG, spaceAfter=6))
    story.append(Paragraph(
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · especially.co · Confidencial",
        ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=GRAY, alignment=TA_CENTER),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
