import calendar

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from Profesores.models import Profesor
from .utils import (
    calcular_pago_base,
    cerrar_periodo as cerrar_periodo_activo,
    crear_periodo,
    dinero_a_texto,
    generar_nomina,
    get_faltas_descontables,
    get_nominas_periodo_activo,
    get_periodo_activo,
    get_profesores_sin_nomina,
    get_todos_los_periodos,
    get_ultimo_periodo,
    marcar_nomina_pagada,
)


def dashboard(request, *args, **kwargs):
    periodo_actual = get_periodo_activo()
    nominas = []

    for nomina in get_nominas_periodo_activo():
        nomina.bruto = nomina.total_bruto
        nomina.neto = nomina.total_neto
        nominas.append(nomina)

    pendientes = get_profesores_sin_nomina()
    for profesor in pendientes:
        profesor.estado = "pendiente"
        profesor.bruto = calcular_pago_base(profesor.id)
        profesor.neto = None
        profesor.profesor = profesor.usuario.get_full_name()
        nominas.append(profesor)

    context = {
        "periodo_label": periodo_actual.display_label() if periodo_actual else None,
        "periodo_actual": periodo_actual,
        "periodos": get_todos_los_periodos(),
        "nominas": nominas,
        "pagos_pendientes": len(pendientes),
        "toast_message": kwargs.get("toast_message"),
        "toast_type": kwargs.get("toast_type"),
    }

    return render(request, "Contabilidad/dashboard.html", context)


def cerrar_periodo(request, periodo_id):
    try:
        periodo = cerrar_periodo_activo(periodo_id)
        messages.success(request, f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} cerrado correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))

    return redirect("contabilidad_dashboard")


def abrir_periodo(request):
    periodo_anterior = get_ultimo_periodo()

    if periodo_anterior is None:
        fecha_inicio = timezone.localdate().replace(day=1)
    elif periodo_anterior.fecha_inicio.day == 1:
        fecha_inicio = periodo_anterior.fecha_fin + timezone.timedelta(days=1)
    else:
        fecha_inicio = timezone.localdate().replace(day=1)

    if fecha_inicio.day == 1:
        fecha_fin = fecha_inicio.replace(day=15)
    else:
        ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
        fecha_fin = fecha_inicio.replace(day=ultimo_dia)

    try:
        periodo = crear_periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        messages.success(request, f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} creado correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))

    return redirect("contabilidad_dashboard")


def procesar_nomina(request, profesor_id):
    nomina = generar_nomina(profesor_id)
    profesor = Profesor.objects.get(id=profesor_id)
    descuento_faltas = get_faltas_descontables(profesor_id)
    total_deducciones = nomina.total_impuestos + nomina.total_deducciones
    total_neto = nomina.total_percepciones - total_deducciones

    context = {
        "nomina": nomina,
        "profesor": profesor,
        "total_faltas": descuento_faltas,
        "periodo_label": f"{nomina.periodo.fecha_inicio:%d} al {nomina.periodo.fecha_fin:%d %B %Y}",
        "preview_total_percepciones": nomina.total_percepciones,
        "preview_total_deducciones": total_deducciones,
        "preview_descuento_faltas": descuento_faltas,
        "preview_total_neto": total_neto,
        "preview_total_neto_texto": dinero_a_texto(total_neto),
    }

    return render(request, "Contabilidad/nomina_gen.html", context)


def pagar_nomina(request, nomina_id):
    try:
        nomina = marcar_nomina_pagada(nomina_id)
        messages.success(request, f"Nomina de {nomina.profesor.usuario.get_full_name()} marcada como pagada.")
    except Exception as exc:
        messages.error(request, str(exc))

    return redirect("contabilidad_dashboard")
