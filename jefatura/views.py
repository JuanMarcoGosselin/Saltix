from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from Asistencias.models import Asistencia, Incidencia
from Profesores.models import Profesor
from users.models import Departamento
from core.decorators import requiere_rol


@login_required
@requiere_rol("jefatura")
def dashboard(request):
    hoy = timezone.localdate()
    
    # Departamentos que tiene a cargo este usuario de jefatura
    departamentos = Departamento.objects.filter(jefe=request.user.id).select_related("plantel")
    dept_ids = [d.id for d in departamentos]

    profesores = (
        Profesor.objects.select_related("usuario")
        .filter(departamentos__id__in=dept_ids)
        .distinct()
        .order_by("usuario__nombre", "usuario__apellido")
    )

    # Semana actual (lunes a viernes)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=4)
    semana_label = f"Semana del {inicio_semana.strftime('%d/%m/%Y')} al {fin_semana.strftime('%d/%m/%Y')}"

    # Incidencias pendientes del equipo
    incidencias_pendientes = (
        Incidencia.objects
        .filter(asistencia__profesor__in=profesores, estado="PENDIENTE")
        .select_related("asistencia__profesor__usuario")
        .order_by("-fecha_solicitud")
    )
    total_pendientes = incidencias_pendientes.count()

    # Asistencias de esta semana para el equipo
    asistencias_semana = (
        Asistencia.objects
        .filter(profesor__in=profesores, fecha__range=(inicio_semana, fin_semana))
        .select_related("profesor__usuario", "horario")
        .order_by("fecha", "hora_entrada")
    )

    # Datos de cada profesor para la tabla del dashboard
    equipo = []
    for profesor in profesores:
        user = profesor.usuario
        equipo.append({
            "id": profesor.id,
            "nombre": f"{user.nombre} {user.apellido}".strip(),
            "puesto": "Profesor",
            "horas_semana": profesor.horario_set.filter(activo=True).count(),
            "estado_label": profesor.get_estado_laboral_display(),
            "estado_clase": "pill-green" if profesor.estado_laboral == "ACTIVO" else "pill-red",
        })

    # Etiquetas de contexto
    depto_label = ", ".join(d.nombre for d in departamentos) if departamentos else "Sin departamento"
    planteles = sorted({d.plantel.nombre for d in departamentos if d.plantel_id})
    ciclo_label = " / ".join(planteles) if planteles else "Sin plantel"

    total_profesores = profesores.count()
    horas_semana_total = sum(p["horas_semana"] for p in equipo)

    context = {
        "fecha_actual": hoy.strftime("%d/%m/%Y"),
        "semana_label": semana_label,
        "departamento_nombre": depto_label,
        "ciclo_label": ciclo_label,

        # Tarjetas del dashboard
        "equipo_total": total_profesores,
        "equipo_variacion": f"{len(departamentos)} departamento(s) a cargo",

        "horas_trabajadas_total": horas_semana_total,
        "horas_trabajadas_promedio": (
            f"{round(horas_semana_total / total_profesores, 1)} horas promedio por profesor"
            if total_profesores else "Sin datos"
        ),

        "solicitudes_pendientes_total": total_pendientes,
        "solicitudes_pendientes_label": (
            f"{total_pendientes} solicitud(es) esperan tu aprobación"
            if total_pendientes > 0
            else "Sin solicitudes pendientes"
        ),

        # Tablas
        "equipo_empleados": equipo,
        "asistencia_registros": list(asistencias_semana),
        "incidencias_registros": list(incidencias_pendientes),
        "profesores_filtro": list(profesores),
    }

    return render(request, "jefatura/dashboard.html", context)