from io import BytesIO

from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Nomina


def generar_reporte_nominas(periodo_id=None):
    """
    Genera un reporte general de nóminas.
    """

    nominas = (
        Nomina.objects
        .select_related(
            "profesor",
            "profesor__usuario",
            "periodo"
        )
        .all()
        .order_by(
            "periodo__fecha_inicio",
            "profesor__usuario__nombre"
        )
    )

    if periodo_id:
        nominas = nominas.filter(periodo_id=periodo_id)

    reporte = []

    for nomina in nominas:

        reporte.append({
            "periodo": (
                f"{nomina.periodo.fecha_inicio} "
                f"- "
                f"{nomina.periodo.fecha_fin}"
            ),

            "profesor": (
                f"{nomina.profesor.usuario.nombre} "
                f"{nomina.profesor.usuario.apellido}"
            ),

            "salario": nomina.total_bruto,

            "penalizaciones": (
                nomina.total_deducciones
            ),

            "neto": nomina.total_neto,
        })

    context = {
        "reporte": reporte,
    }

    html_string = render_to_string(
        "Contabilidad/reports/reporte_nominas.html",
        context
    )

    pdf_file = BytesIO()

    HTML(
        string=html_string
    ).write_pdf(pdf_file)

    pdf_file.seek(0)

    return pdf_file.getvalue()