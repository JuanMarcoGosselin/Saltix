from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from Asistencias.services import (
    apply_asistencia_filters,
    apply_incidencia_filters,
    get_user_departamentos,
    paginate_queryset,
    scope_asistencias_for_user,
    scope_incidencias_for_user,
)
from Profesores.models import Profesor
from core.decorators import requiere_rol


@login_required
@requiere_rol("jefatura")
def dashboard(request):
    hoy = timezone.localdate()
    departamentos = list(get_user_departamentos(request.user))
    dept_ids = [depto.id for depto in departamentos]

    profesores_qs = (
        Profesor.objects.select_related("usuario")
        .filter(departamentos__id__in=dept_ids)
        .distinct()
        .order_by("usuario__nombre", "usuario__apellido")
    )

    asistencias_qs = scope_asistencias_for_user(request.user)
    incidencias_qs = scope_incidencias_for_user(request.user)
    incidencias_pendientes_qs = apply_incidencia_filters(incidencias_qs, estado="PENDIENTE")

    asistencias_page = paginate_queryset(asistencias_qs, page=1, page_size=10)
    incidencias_page = paginate_queryset(incidencias_pendientes_qs, page=1, page_size=10)

    equipo_empleados = []
    for profesor in profesores_qs:
        user = profesor.usuario
        equipo_empleados.append(
            {
                "id": profesor.id,
                "nombre": f"{user.nombre} {user.apellido}".strip(),
                "puesto": "Profesor",
                "horas_semana": profesor.horario_set.filter(activo=True).count(),
                "estado_label": profesor.get_estado_laboral_display(),
                "estado_clase": "pill-green" if profesor.estado_laboral == "ACTIVO" else "pill-red",
            }
        )

    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=4)
    semana_label = f"Semana del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"

    total_horas_semana = asistencias_qs.filter(fecha__range=(inicio_semana, fin_semana)).count()
    depto_label = ", ".join(depto.nombre for depto in departamentos) if departamentos else "Sin departamento"
    planteles = sorted({depto.plantel.nombre for depto in departamentos if depto.plantel_id})
    ciclo_label = " / ".join(planteles) if planteles else "Sin plantel"

    context = {
        "fecha_actual": hoy.strftime("%d/%m/%Y"),
        "departamento_nombre": depto_label,
        "ciclo_label": ciclo_label,
        "equipo_total": profesores_qs.count(),
        "equipo_variacion": f"{len(departamentos)} departamento(s) a cargo",
        "horas_trabajadas_total": total_horas_semana,
        "horas_trabajadas_promedio": f"{round(total_horas_semana / profesores_qs.count(), 1) if profesores_qs.count() else 0} registros por profesor",
        "solicitudes_pendientes_total": incidencias_pendientes_qs.count(),
        "solicitudes_pendientes_label": (
            f"{incidencias_pendientes_qs.count()} solicitud(es) esperan tu aprobacion"
            if incidencias_pendientes_qs.exists()
            else "Sin solicitudes pendientes"
        ),
        "equipo_empleados": equipo_empleados,
        "asistencia_registros": asistencias_page.items,
        "incidencias_registros": incidencias_page.items,
        "profesores_filtro": list(profesores_qs),
        "week_label": semana_label,
        "semana_label": semana_label,
    }
    return render(request, "jefatura/dashboard.html", context)
