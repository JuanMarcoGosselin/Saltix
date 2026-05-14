import csv
import io
from datetime import datetime, time
from html import escape
from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from Asistencias.models import Asistencia, Incidencia
from Contabilidad.utils import horas_de_clase
from Profesores.models import Horario, Profesor
from users.models import Departamento


DIAS_ORDEN = {"LUN": 1, "MAR": 2, "MIE": 3, "JUE": 4, "VIE": 5, "SAB": 6}
HORAS_HORARIO = list(range(6, 24))
REPORTES = {
    "asistencias_profesor": "Asistencias por profesor",
    "incidencias": "Incidencias",
    "cumplimiento": "Cumplimiento docente",
    "carga": "Carga academica",
    "horarios": "Horarios",
    "faltas_recurrentes": "Faltas recurrentes",
    "departamento": "Departamento",
    "asistencia_diaria": "Asistencia diaria/semanal",
    "historico": "Historico",
    "nomina": "Nomina limitado",
}


def parse_date(value, default=None):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return default


def parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (TypeError, ValueError):
        return None


def rol_usuario(user):
    rol = getattr(getattr(user, "rol_id", None), "nombre", "") or ""
    return rol.lower()


def departamentos_jefe(user):
    if rol_usuario(user) in {"administrador", "admin"}:
        return Departamento.objects.select_related("plantel").filter(activo=True)
    return Departamento.objects.select_related("plantel").filter(jefe=user, activo=True)


def departamentos_destino_transferencia(user):
    qs = Departamento.objects.select_related("plantel", "jefe").filter(activo=True)
    if rol_usuario(user) in {"administrador", "admin"}:
        return qs.order_by("nombre")
    return qs.exclude(jefe=user).order_by("nombre")


def profesores_base(user):
    departamentos = departamentos_jefe(user)
    return (
        Profesor.objects
        .select_related("usuario", "departamento", "plantel")
        .filter(departamento__in=departamentos)
        .distinct()
        .order_by("usuario__nombre", "usuario__apellido")
    )


def filtrar_profesores(qs, params):
    profesor = (params.get("profesor") or "").strip()
    estado = (params.get("estado_laboral") or "").strip()

    if profesor:
        qs = qs.filter(
            Q(usuario__nombre__icontains=profesor)
            | Q(usuario__apellido__icontains=profesor)
            | Q(rfc__icontains=profesor)
        )
    if estado:
        qs = qs.filter(estado_laboral=estado)
    return qs


def profesor_permitido(user, profesor_id):
    return profesores_base(user).filter(id=profesor_id).first()


def asistencias_scope(user):
    return (
        Asistencia.objects
        .select_related("profesor", "profesor__usuario", "profesor__departamento", "profesor__plantel", "horario")
        .filter(profesor__in=profesores_base(user))
        .exclude(tipo_registro="COMPENSATORIA")
    )


def incidencias_scope(user):
    return (
        Incidencia.objects
        .select_related("asistencia", "asistencia__profesor", "asistencia__profesor__usuario", "aprobador")
        .filter(asistencia__profesor__in=profesores_base(user))
    )


def asistencia_stats(qs):
    aprobadas = Incidencia.objects.filter(
        asistencia__in=qs,
        estado="APROBADA",
    ).values_list("asistencia_id", flat=True)
    return {
        "asistencias": qs.filter(estado="ASISTENCIA", cancelada_institucional=False).count(),
        "retardos": qs.filter(estado="RETARDO", cancelada_institucional=False).exclude(id__in=aprobadas).count(),
        "faltas": qs.filter(estado="FALTA", justificada=False, cancelada_institucional=False).exclude(id__in=aprobadas).count(),
        "justificadas": qs.filter(Q(justificada=True) | Q(id__in=aprobadas)).count(),
        "canceladas": qs.filter(cancelada_institucional=True).count(),
    }


def horario_conflictos(profesor, horario=None, dia=None, inicio=None, fin=None):
    qs = Horario.objects.filter(profesor=profesor, activo=True)
    if horario:
        qs = qs.exclude(id=horario.id)
        dia = dia or horario.dia_semana
        inicio = inicio or horario.hora_inicio
        fin = fin or horario.hora_fin
    return qs.filter(dia_semana=dia, hora_inicio__lt=fin, hora_fin__gt=inicio).exists()


def dashboard_redirect(page, ok=None, error=None):
    url = reverse("jefatura_dashboard")
    params = {}
    if page:
        params["page"] = page
    if ok:
        params["ok"] = ok
    if error:
        params["error"] = error
    return redirect(f"{url}?{urlencode(params)}" if params else url)


def asistencias_scope_for_profesor(profesor, inicio, fin):
    return Asistencia.objects.filter(
        profesor=profesor,
        fecha__range=(inicio, fin),
    ).exclude(tipo_registro="COMPENSATORIA")


def horario_grid(horarios):
    grid = []
    for hora in HORAS_HORARIO:
        dias = []
        for code, label in Horario.DIAS:
            checked = any(
                h.dia_semana == code
                and h.hora_inicio <= time(hour=hora)
                and h.hora_fin > time(hour=hora)
                for h in horarios
            )
            dias.append({"code": code, "label": label, "checked": checked})
        grid.append({"hora": hora, "dias": dias})
    return grid


def agrupar_slots_horario(slots):
    by_day = {}
    for slot in slots:
        try:
            day, hour = slot.split("|", 1)
            hour = int(hour)
        except (ValueError, TypeError):
            continue
        if day not in DIAS_ORDEN or hour not in HORAS_HORARIO:
            continue
        by_day.setdefault(day, set()).add(hour)

    bloques = []
    for day in sorted(by_day, key=lambda item: DIAS_ORDEN[item]):
        hours = sorted(by_day[day])
        i = 0
        while i < len(hours):
            start = hours[i]
            end = start + 1
            i += 1
            while i < len(hours) and hours[i] == end:
                end += 1
                i += 1
            bloques.append({
                "dia_semana": day,
                "hora_inicio": time(hour=start),
                "hora_fin": time(hour=23, minute=59) if end >= 24 else time(hour=end),
                "aula": "",
                "es_hora_clase": True,
            })
    return bloques


def reemplazar_horarios_profesor(profesor, slots):
    bloques = agrupar_slots_horario(slots)
    if not bloques:
        return False

    profesor.horario_set.update(activo=False)
    for bloque in bloques:
        horario, created = Horario.objects.get_or_create(
            profesor=profesor,
            dia_semana=bloque["dia_semana"],
            hora_inicio=bloque["hora_inicio"],
            hora_fin=bloque["hora_fin"],
            defaults={
                "aula": bloque["aula"],
                "es_hora_clase": bloque["es_hora_clase"],
                "activo": True,
            },
        )
        if not created:
            horario.aula = bloque["aula"]
            horario.es_hora_clase = bloque["es_hora_clase"]
            horario.activo = True
            horario.save(update_fields=["aula", "es_hora_clase", "activo"])
    return True


def profesor_row(profesor, inicio, fin):
    asistencias = asistencias_scope_for_profesor(profesor, inicio, fin)
    stats = asistencia_stats(asistencias)
    horarios = list(profesor.horario_set.filter(activo=True).order_by("dia_semana", "hora_inicio"))
    recientes = (
        Incidencia.objects
        .filter(asistencia__profesor=profesor)
        .order_by("-fecha_solicitud")[:2]
    )
    return {
        "profesor": profesor,
        "stats": stats,
        "horarios": horarios,
        "horario_grid": horario_grid(horarios),
        "horas_asignadas": sum(round(horas_de_clase(h), 2) for h in horarios),
        "incidencias_recientes": recientes,
    }


def export_rows(rows, columns, title, formato):
    if formato == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row.get(col, "") for col in columns])
        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{title}.csv"'
        return response

    if formato == "excel":
        body = ["<table><thead><tr>"]
        body.extend(f"<th>{escape(col)}</th>" for col in columns)
        body.append("</tr></thead><tbody>")
        for row in rows:
            body.append("<tr>")
            body.extend(f"<td>{escape(str(row.get(col, '')))}</td>" for col in columns)
            body.append("</tr>")
        body.append("</tbody></table>")
        response = HttpResponse("".join(body), content_type="application/vnd.ms-excel; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{title}.xls"'
        return response

    pdf_lines = [title.replace("_", " ").title(), ""]
    pdf_lines.append(" | ".join(columns))
    for row in rows:
        pdf_lines.append(" | ".join(str(row.get(col, "")) for col in columns))
    pdf = simple_pdf("\n".join(pdf_lines[:80]))
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{title}.pdf"'
    return response


def simple_pdf(text):
    lines = text.splitlines()
    stream = ["BT", "/F1 10 Tf", "50 790 Td"]
    first = True
    for line in lines:
        clean = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:110]
        if first:
            stream.append(f"({clean}) Tj")
            first = False
        else:
            stream.append(f"0 -14 Td ({clean}) Tj")
    stream.append("ET")
    stream_data = "\n".join(stream).encode("latin-1", errors="replace")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream_data)).encode() + b" >> stream\n" + stream_data + b"\nendstream endobj\n",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return output.getvalue()
