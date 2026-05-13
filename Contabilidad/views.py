from django.shortcuts import render
from django.http import HttpResponse
from .reports import generar_reporte_nominas


def dashboard(request):
    return render(request, "Contabilidad/dashboard.html")


def reporte_nominas_pdf(request):
    periodo_id = request.GET.get("periodo")

    pdf = generar_reporte_nominas(periodo_id)

    response = HttpResponse(
        pdf,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="reporte_nominas.pdf"'
    )

    return response