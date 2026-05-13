from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .utils import *
import calendar
import locale
locale.setlocale(locale.LC_TIME, 'Spanish_Mexico')

def dashboard(request, *args, **kwargs):
    periodo_actual = get_active_periodo()
    periodos = get_all_periodos()
    nominas = []
    nominas_periodo = get_nominas_from_period()
    nominas_pendientes = get_pending_nomina()

    for nomina in nominas_periodo:
        nomina.bruto = nomina.total_bruto
        nominas.append(nomina)

    for nomina in nominas_pendientes:
        nomina.estado = "pendiente"
        nomina.bruto = calculate_base_payment(nomina.id)
        nomina.profesor = nomina.usuario.get_full_name()
        nominas.append(nomina)

    pending_nominas = len(nominas_pendientes)

    context = {
        "periodo_label": f"{periodo_actual.fecha_inicio.strftime('%d %B')} - {periodo_actual.fecha_fin.strftime('%d %B')}" if periodo_actual else None,
        "periodo_actual": periodo_actual,
        "periodos": periodos,
        "nominas": nominas,
        "pagos_pendientes": pending_nominas,
        "toast_message": kwargs.get("toast_message"),
        "toast_type": kwargs.get("toast_type"),
    }

    return render(request, "Contabilidad/dashboard.html", context)


def cerrar_periodo(request, periodo_id):
    # Funcion para cerrar un periodo. Solo se puede cerrar un periodo abierto.
    try:
        periodo = deactivate_periodo(periodo_id)
        message = f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} cerrado correctamente."
        messages.success(request, message)
    except Exception as exc:
        message = str(exc)
        messages.error(request, message)

    return redirect("contabilidad_dashboard")


def abrir_periodo(request):
    # Funcion para abrir un nuevo periodo. Solo se puede abrir un periodo si no hay otro abierto.
    periodo_anterior = get_last_periodo()

    # Si es el primer periodo del mes, se abre del dia 1 al 15. Si es el segundo periodo del mes, se abre del dia 16 al ultimo dia del mes.
    if periodo_anterior is None:
        fecha_inicio = timezone.now().date().replace(day=1)
    elif periodo_anterior.fecha_inicio.day == 1:
        fecha_inicio = periodo_anterior.fecha_fin + timezone.timedelta(days=1)
    else:
        fecha_inicio = timezone.now().date().replace(day=1)

    if fecha_inicio.day == 1:
        fecha_fin = fecha_inicio.replace(day=15)
    else:
        ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
        fecha_fin = fecha_inicio.replace(day=ultimo_dia)

    try:
        periodo = create_periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        message = f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} creado correctamente."
        messages.success(request, message)
    except Exception as exc:
        message = str(exc)
        messages.error(request, message)

    return redirect("contabilidad_dashboard")

def procesar_nomina(request, profesor_id):
    nomina = get_nomina_for_profesor(profesor_id)
    profesor = Profesor.objects.get(id=profesor_id)
    total_faltas = get_total_faltas(profesor_id)
    periodo_label = f"{nomina.periodo.fecha_inicio.strftime('%d')} al {nomina.periodo.fecha_fin.strftime('%d %B %Y')}"
    preview_total_percepciones = nomina.total_percepciones
    preview_descuento_faltas = get_deducciones_faltas(profesor_id)
    preview_total_deducciones = nomina.total_impuestos + nomina.total_deducciones
    preview_total_neto = preview_total_percepciones - preview_total_deducciones
    context = {
        "nomina": nomina,
        "profesor": profesor,
        "total_faltas": total_faltas,
        "periodo_label": periodo_label,
        "preview_total_percepciones": preview_total_percepciones,
        "preview_total_deducciones": preview_total_deducciones,
        "preview_descuento_faltas": preview_descuento_faltas,
        "preview_total_neto": preview_total_neto,
        "preview_total_neto_texto": money_to_spanish_text(preview_total_neto),
    }    

    return render(request, "Contabilidad/nomina_gen.html", context)

def pagar_nomina(request, nomina_id):
    # Funcion para marcar una nomina como pagada. Solo se puede marcar como pagada una nomina que este pendiente.
    try:
        nomina = mark_nomina_as_paid(nomina_id)
        message = f"Nómina de {nomina.profesor.usuario.get_full_name()} marcada como pagada."
        messages.success(request, message)
    except Exception as exc:
        message = str(exc)
        messages.error(request, message)

    return redirect("contabilidad_dashboard")
def reporte_nominas_pdf(request):
    from .reports import generar_reporte_nominas

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
