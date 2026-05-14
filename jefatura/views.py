from datetime import timedelta

from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from Contabilidad.utils import horas_de_asistencia, horas_de_clase
from Profesores.models import Horario, Profesor
from users.models import Departamento
from core.decorators import requiere_rol
from .models import SolicitudTransferencia
from .utils import *


@requiere_rol("jefatura", "administrador")
def dashboard(request):
    hoy = timezone.localdate()
    fecha_dia = parse_date(request.GET.get("fecha"), hoy)
    dia_anterior = fecha_dia - timedelta(days=1)
    dia_siguiente = fecha_dia + timedelta(days=1)
    inicio_mes = fecha_dia.replace(day=1)
    fin_mes = fecha_dia

    departamentos = list(departamentos_jefe(request.user))
    profesores_qs = filtrar_profesores(profesores_base(request.user), request.GET)
    profesores = list(profesores_qs)
    asistencias_dia = asistencias_scope(request.user).filter(fecha=fecha_dia)
    if request.GET.get("asistencia_profesor"):
        asistencias_dia = asistencias_dia.filter(profesor_id=request.GET["asistencia_profesor"])
    if request.GET.get("asistencia_estado"):
        estado = request.GET["asistencia_estado"]
        asistencias_dia = asistencias_dia.filter(cancelada_institucional=True) if estado == "CANCELADA" else asistencias_dia.filter(estado=estado)

    incidencias = incidencias_scope(request.user).order_by("-fecha_solicitud", "-id")
    incidencias_pendientes = incidencias.filter(estado="PENDIENTE")
    transferencias = (
        SolicitudTransferencia.objects
        .select_related("profesor", "profesor__usuario", "departamento_origen", "departamento_destino", "plantel_origen", "plantel_destino", "solicitante", "responsable")
        .filter(Q(departamento_origen__in=departamentos) | Q(departamento_destino__in=departamentos))
        .distinct()
        .order_by("-fecha_solicitud", "-id")
    )
    transferencias_recibidas = transferencias.filter(departamento_destino__in=departamentos)
    transferencias_realizadas = transferencias.filter(departamento_origen__in=departamentos)
    profesores_transferibles = (
        profesores_qs
        .exclude(solicitudes_transferencia__estado="PENDIENTE")
        .distinct()
    )

    context = {
        "fecha_actual": hoy.strftime("%d/%m/%Y"),
        "fecha_dia": fecha_dia,
        "dia_anterior": dia_anterior,
        "dia_siguiente": dia_siguiente,
        "departamentos": departamentos,
        "departamentos_destino_transferencia": list(departamentos_destino_transferencia(request.user)),
        "profesores": profesores,
        "profesores_transferibles": list(profesores_transferibles),
        "equipo_rows": [profesor_row(p, inicio_mes, fin_mes) for p in profesores],
        "asistencias_dia": asistencias_dia.prefetch_related("incidencias").order_by("profesor__usuario__nombre", "horario__hora_inicio"),
        "asistencia_stats_dia": asistencia_stats(asistencias_dia),
        "incidencias": incidencias[:40],
        "incidencias_pendientes": incidencias_pendientes,
        "solicitudes_pendientes_total": incidencias_pendientes.count() + transferencias.filter(estado="PENDIENTE").count(),
        "transferencias_recibidas": transferencias_recibidas[:30],
        "transferencias_realizadas": transferencias_realizadas[:30],
        "transferencias_historial": transferencias.exclude(estado="PENDIENTE")[:30],
        "reportes": REPORTES,
        "estados_profesor": Profesor.ESTADOS,
        "dias_horario": Horario.DIAS,
        "ok": request.GET.get("ok"),
        "error": request.GET.get("error"),
        "initial_page": request.GET.get("page", "equipo"),
    }
    return render(request, "jefatura/dashboard.html", context)


@requiere_rol("jefatura", "administrador")
def guardar_horario(request):
    if request.method != "POST":
        return dashboard_redirect("equipo")
    profesor = profesor_permitido(request.user, request.POST.get("profesor_id"))
    if not profesor:
        return dashboard_redirect("equipo", error="Profesor no permitido.")

    if not reemplazar_horarios_profesor(profesor, request.POST.getlist("horario_slot")):
        return dashboard_redirect("equipo", error="Selecciona al menos un bloque de horario.")
    return dashboard_redirect("equipo", ok="Horario guardado.")


@requiere_rol("jefatura", "administrador")
def eliminar_horario(request):
    if request.method != "POST":
        return dashboard_redirect("equipo")
    profesor = profesor_permitido(request.user, request.POST.get("profesor_id"))
    horario = Horario.objects.filter(id=request.POST.get("horario_id"), profesor=profesor).first() if profesor else None
    if not horario:
        return dashboard_redirect("equipo", error="Horario no encontrado.")
    horario.activo = False
    horario.save(update_fields=["activo"])
    return dashboard_redirect("equipo", ok="Horario eliminado.")


@requiere_rol("jefatura", "administrador")
def crear_transferencia(request):
    if request.method != "POST":
        return dashboard_redirect("solicitudes")
    profesor = profesor_permitido(request.user, request.POST.get("profesor_id"))
    destino = Departamento.objects.select_related("plantel").filter(id=request.POST.get("departamento_destino_id"), activo=True).first()
    motivo = (request.POST.get("motivo") or "").strip()
    if not profesor or not destino or not motivo:
        return dashboard_redirect("solicitudes", error="Datos de transferencia incompletos.")
    if profesor.departamento_id == destino.id and profesor.plantel_id == destino.plantel_id:
        return dashboard_redirect("solicitudes", error="El profesor ya pertenece a ese departamento y plantel.")
    if rol_usuario(request.user) not in {"administrador", "admin"} and destino.jefe_id == request.user.id:
        return dashboard_redirect("solicitudes", error="Selecciona un departamento destino de otro jefe.")
    if SolicitudTransferencia.objects.filter(profesor=profesor, estado="PENDIENTE").exists():
        return dashboard_redirect("solicitudes", error="Ese profesor ya tiene una transferencia pendiente.")

    SolicitudTransferencia.objects.create(
        profesor=profesor,
        departamento_origen=profesor.departamento,
        departamento_destino=destino,
        plantel_origen=profesor.plantel,
        plantel_destino=destino.plantel,
        motivo=motivo,
        solicitante=request.user,
    )
    return dashboard_redirect("solicitudes", ok="Transferencia creada.")


@requiere_rol("jefatura", "administrador")
def resolver_transferencia(request):
    if request.method != "POST":
        return dashboard_redirect("solicitudes")
    departamentos = departamentos_jefe(request.user)
    transferencia = (
        SolicitudTransferencia.objects
        .select_related("profesor", "departamento_destino", "plantel_destino")
        .filter(id=request.POST.get("transferencia_id"), departamento_destino__in=departamentos)
        .first()
    )
    accion = request.POST.get("accion")
    if not transferencia or transferencia.estado != "PENDIENTE":
        return dashboard_redirect("solicitudes", error="Transferencia no disponible.")
    if accion not in {"APROBADA", "RECHAZADA"}:
        return dashboard_redirect("solicitudes", error="Accion invalida.")

    transferencia.estado = accion
    transferencia.responsable = request.user
    transferencia.observaciones = (request.POST.get("observaciones") or "").strip()
    transferencia.fecha_resolucion = timezone.now()
    transferencia.save(update_fields=["estado", "responsable", "observaciones", "fecha_resolucion"])

    if accion == "APROBADA":
        profesor = transferencia.profesor
        profesor.departamento = transferencia.departamento_destino
        profesor.plantel = transferencia.plantel_destino
        profesor.save(update_fields=["departamento", "plantel"])
    return dashboard_redirect("solicitudes", ok="Transferencia resuelta.")


@requiere_rol("jefatura", "administrador")
def cancelar_transferencia(request):
    if request.method != "POST":
        return dashboard_redirect("solicitudes")
    transferencia = (
        SolicitudTransferencia.objects
        .filter(
            id=request.POST.get("transferencia_id"),
            solicitante=request.user,
            estado="PENDIENTE",
        )
        .first()
    )
    if not transferencia:
        return dashboard_redirect("solicitudes", error="Solo puedes cancelar solicitudes pendientes creadas por ti.")

    transferencia.estado = "CANCELADA"
    transferencia.responsable = request.user
    transferencia.observaciones = (request.POST.get("observaciones") or "Cancelada por el solicitante.").strip()
    transferencia.fecha_resolucion = timezone.now()
    transferencia.save(update_fields=["estado", "responsable", "observaciones", "fecha_resolucion"])
    return dashboard_redirect("solicitudes", ok="Transferencia cancelada.")


@requiere_rol("jefatura", "administrador")
def reporte_jefatura(request):
    tipo = request.GET.get("tipo", "departamento")
    formato = request.GET.get("formato", "csv")
    if tipo not in REPORTES:
        tipo = "departamento"
    if formato not in {"csv", "excel", "pdf"}:
        formato = "csv"

    inicio = parse_date(request.GET.get("inicio"), timezone.localdate().replace(day=1))
    fin = parse_date(request.GET.get("fin"), timezone.localdate())
    profesor_id = request.GET.get("profesor_id")
    profesores = profesores_base(request.user)
    if profesor_id:
        profesores = profesores.filter(id=profesor_id)
    asistencias = asistencias_scope(request.user).filter(fecha__range=(inicio, fin), profesor__in=profesores)
    incidencias = incidencias_scope(request.user).filter(fecha_solicitud__date__range=(inicio, fin), asistencia__profesor__in=profesores)

    rows = []
    columns = ["Profesor", "Departamento", "Plantel", "Asistencias", "Retardos", "Faltas", "Justificadas", "Canceladas", "Total", "Porcentaje"]
    for profesor in profesores:
        qs = asistencias.filter(profesor=profesor)
        stats = asistencia_stats(qs)
        total = sum(stats.values())
        porcentaje = round((stats["asistencias"] + stats["justificadas"]) * 100 / total, 2) if total else 0
        base = {
            "Profesor": profesor.usuario.get_full_name(),
            "Departamento": profesor.departamento.nombre,
            "Plantel": profesor.plantel.nombre,
            "Asistencias": stats["asistencias"],
            "Retardos": stats["retardos"],
            "Faltas": stats["faltas"],
            "Justificadas": stats["justificadas"],
            "Canceladas": stats["canceladas"],
            "Total": total,
            "Porcentaje": f"{porcentaje}%",
        }
        if tipo == "incidencias":
            base.update({
                "Pendientes": incidencias.filter(asistencia__profesor=profesor, estado="PENDIENTE").count(),
                "Aprobadas": incidencias.filter(asistencia__profesor=profesor, estado="APROBADA").count(),
                "Rechazadas": incidencias.filter(asistencia__profesor=profesor, estado="RECHAZADA").count(),
            })
            columns = list(base.keys())
        elif tipo == "carga":
            horarios = Horario.objects.filter(profesor=profesor, activo=True)
            horas_asignadas = sum(horas_de_clase(h) for h in horarios)
            horas_impartidas = sum(horas_de_asistencia(a) for a in qs.filter(estado__in=["ASISTENCIA", "RETARDO"]))
            base.update({"Horas asignadas": round(horas_asignadas, 2), "Horas impartidas": round(horas_impartidas, 2), "Diferencia": round(horas_asignadas - horas_impartidas, 2)})
            columns = list(base.keys())
        elif tipo == "horarios":
            horarios = Horario.objects.filter(profesor=profesor, activo=True)
            base.update({"Horarios activos": horarios.count(), "Materias/Aulas": ", ".join(f"{h.dia_semana} {h.aula}" for h in horarios[:5])})
            columns = list(base.keys())
        elif tipo == "faltas_recurrentes":
            dias = qs.filter(estado__in=["FALTA", "RETARDO"]).values("fecha").annotate(total=Count("id")).order_by("-total", "fecha")[:3]
            base.update({"Dias con incidencias": ", ".join(f"{d['fecha']} ({d['total']})" for d in dias)})
            columns = list(base.keys())
        elif tipo == "nomina":
            horas = sum(horas_de_asistencia(a) for a in qs.filter(estado__in=["ASISTENCIA", "RETARDO"]))
            base = {
                "Profesor": profesor.usuario.get_full_name(),
                "Retardos": stats["retardos"],
                "Faltas": stats["faltas"],
                "Horas trabajadas": round(horas, 2),
                "Incidencias aprobadas": incidencias.filter(asistencia__profesor=profesor, estado="APROBADA").count(),
            }
            columns = list(base.keys())
        rows.append(base)

    return export_rows(rows, columns, f"jefatura_{tipo}_{inicio}_{fin}", formato)
