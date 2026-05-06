from django.contrib import messages
from django.shortcuts import redirect, render
from .utils import *
import calendar

def dashboard(request, *args, **kwargs):
    periodo_actual = get_active_periodo()
    periodos = get_all_periodos()
    nominas = []
    nominas_periodo = get_nominas_from_period()
    nominas_pendientes = get_pending_nomina()

    for nomina in nominas_periodo:
        nomina.estado = "pagada"
        nomina.bruto = nomina.total_bruto
        nominas.append(nomina)

    for nomina in nominas_pendientes:
        nomina.estado = "pendiente"
        nomina.bruto = calculate_base_payment(nomina.id)
        nomina.profesor = nomina.usuario.get_full_name()
        nominas.append(nomina)

    context = {
        "periodo_actual": periodo_actual,
        "periodos": periodos,
        "nominas": nominas,
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

def pagar_nomina(request, profesor_id):
    pass
    # Funcion para generar la nomina de un profesor. Solo se puede generar la nomina si el periodo esta abierto.
    try:
        nomina = generate_nomina_for_profesor(profesor_id)
        message = f"Nómina de {nomina.profesor} generada correctamente."
        messages.success(request, message)
    except Exception as exc:
        message = str(exc)
        messages.error(request, message)

    return redirect("contabilidad_dashboard")