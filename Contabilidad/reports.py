from io import BytesIO
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


from .models import Nomina


def generar_reporte_nominas(periodo_id=None):

    nominas = (
        Nomina.objects
        .select_related(
            "profesor",
            "profesor__usuario",
            "periodo"
        )
        .order_by(
            "periodo__fecha_inicio",
            "profesor__usuario__nombre"
        )
    )

    if periodo_id:
        nominas = nominas.filter(periodo_id=periodo_id)

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elementos = []

    titulo = Paragraph(
        "Reporte General de Nómina",
        styles["Title"]
    )

    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    datos = [[
        "Periodo",
        "Profesor",
        "Salario",
        "Penalizaciones",
        "Neto"
    ]]

    total_general = Decimal("0.00")

    for nomina in nominas:

        periodo = (
            f"{nomina.periodo.fecha_inicio.strftime('%d/%m/%Y')} - "
            f"{nomina.periodo.fecha_fin.strftime('%d/%m/%Y')}"
        )

        profesor = (
            f"{nomina.profesor.usuario.nombre} "
            f"{nomina.profesor.usuario.apellido}"
        )

        bruto = nomina.total_bruto
        deducciones = nomina.total_deducciones
        neto = nomina.total_neto

        total_general += neto

        datos.append([
            periodo,
            profesor,
            f"${bruto:,.2f}",
            f"${deducciones:,.2f}",
            f"${neto:,.2f}",
        ])

    datos.append([
        "",
        "",
        "",
        "TOTAL",
        f"${total_general:,.2f}"
    ])

    tabla = Table(
        datos,
        colWidths=[
            4.5 * cm,
            6 * cm,
            3 * cm,
            3.5 * cm,
            3 * cm
        ]
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
