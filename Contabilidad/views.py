from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.decorators import requiere_rol
from Notifications.utils import notify_role, notify_user
from Profesores.models import Profesor

from .models import DetalleNomina, Nomina, Periodo
from .utils import (
    agregar_concepto_nomina,
    calcular_pago_base,
    cerrar_nomina as cerrar_nomina_activa,
    cerrar_periodo as cerrar_periodo_activo,
    crear_periodo_actual,
    dinero_a_texto,
    eliminar_concepto_nomina,
    generar_nomina_profesor,
    generar_nominas_periodo,
    generar_contexto_recibo,
    generar_texto_recibo,
    generar_texto_reporte_periodo,
    obtener_nominas_periodo,
    get_periodo_activo,
    get_profesores_sin_nomina,
    get_todos_los_periodos,
    marcar_nomina_pagada,
    obtener_resumen_periodo,
    obtener_totales_periodo,
    puede_generar_recibo,
    regenerar_nomina_profesor,
    regenerar_nominas_periodo,
    resumen_nomina,
    simple_pdf,
)


def _notify_error_admin(message):
    notify_role(
        "admin",
        "Inconsistencia en nomina",
        message,
        "danger",
        "/panel-admin/?page=inicio",
    )


def _user_role(user):
    rol = getattr(user, "rol_id", None)
    return (getattr(rol, "nombre", "") or "").lower()


def _pdf_response(text, filename, download=False):
    response = HttpResponse(simple_pdf(text), content_type="application/pdf")
    disposition = "attachment" if download else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response


@login_required
@requiere_rol("contabilidad", "administrador")
def dashboard(request, *args, **kwargs):
    periodo_actual = get_periodo_activo()
    nominas = []

    nominas_qs = Nomina.objects.select_related("profesor", "profesor__usuario", "periodo")
    if periodo_actual:
        nominas_qs = nominas_qs.filter(periodo=periodo_actual)
    else:
        nominas_qs = nominas_qs.none()

    for nomina in nominas_qs:
        nomina.bruto = nomina.total_bruto
        nomina.neto = nomina.total_neto
        nominas.append(nomina)

    pendientes = []
    if periodo_actual and periodo_actual.estado == "ABIERTO":
        pendientes = get_profesores_sin_nomina()
        for profesor in pendientes:
            profesor.estado = "pendiente"
            profesor.bruto = calcular_pago_base(profesor.id, periodo_actual)
            profesor.neto = None
            profesor.profesor = profesor.usuario.get_full_name()
            nominas.append(profesor)

    historial_qs = Nomina.objects.select_related(
        "profesor",
        "profesor__usuario",
        "periodo",
    ).filter(estado__in=["cerrada", "pagada"])

    periodos_historial = get_todos_los_periodos()
    if periodo_actual:
        historial_qs = historial_qs.filter(periodo__fecha_fin__lt=periodo_actual.fecha_inicio)
        periodos_historial = periodos_historial.filter(fecha_fin__lt=periodo_actual.fecha_inicio)

    estado = request.GET.get("estado") or ""
    profesor_id = request.GET.get("profesor") or ""
    periodo_id = request.GET.get("periodo") or ""
    if estado:
        historial_qs = historial_qs.filter(estado=estado)
    if profesor_id:
        historial_qs = historial_qs.filter(profesor_id=profesor_id)
    if periodo_id:
        historial_qs = historial_qs.filter(periodo_id=periodo_id)

    context = {
        "periodo_label": periodo_actual.display_label() if periodo_actual else None,
        "periodo_actual": periodo_actual,
        "periodos": get_todos_los_periodos(),
        "periodos_historial": periodos_historial,
        "profesores": Profesor.objects.select_related("usuario").order_by("usuario__nombre"),
        "nominas": nominas,
        "historial_nominas": historial_qs.order_by("-fecha_actualizacion", "-id"),
        "pagos_pendientes": len(pendientes),
        "selected_estado": estado,
        "selected_profesor": profesor_id,
        "selected_periodo": periodo_id,
        "toast_message": kwargs.get("toast_message"),
        "toast_type": kwargs.get("toast_type"),
    }

    return render(request, "Contabilidad/dashboard.html", context)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def cerrar_periodo(request, periodo_id):
    try:
        periodo = cerrar_periodo_activo(periodo_id)
        notify_role(
            "contabilidad",
            "Nomina cerrada",
            f"El periodo {periodo.fecha_inicio} - {periodo.fecha_fin} fue cerrado.",
            "success",
            "/contabilidad/",
        )
        messages.success(request, f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} cerrado correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))
        _notify_error_admin(str(exc))

    return redirect("contabilidad_dashboard")


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def abrir_periodo(request):
    try:
        periodo = crear_periodo_actual()
        messages.success(request, f"Periodo {periodo.fecha_inicio} - {periodo.fecha_fin} creado correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))

    return redirect("contabilidad_dashboard")


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def procesar_nomina(request, profesor_id):
    try:
        nomina = generar_nomina_profesor(profesor_id)
        profesor = nomina.profesor
        notify_user(
            profesor.usuario,
            "Nomina disponible",
            "Tu nomina fue generada y esta disponible para revision.",
            "success",
            "/profesores/?page=recibos",
        )
        notify_role(
            "contabilidad",
            "Nomina lista para revision",
            f"Se genero la nomina de {profesor.usuario.get_full_name()}.",
            "info",
            "/contabilidad/",
        )
        return redirect("detalle_nomina", nomina_id=nomina.id)
    except Exception as exc:
        messages.error(request, str(exc))
        _notify_error_admin(str(exc))
        return redirect("contabilidad_dashboard")


@login_required
@requiere_rol("contabilidad", "administrador")
def detalle_nomina(request, nomina_id):
    nomina = get_object_or_404(
        Nomina.objects.select_related("profesor", "profesor__usuario", "periodo"),
        id=nomina_id,
    )
    profesor = nomina.profesor
    detalles = DetalleNomina.objects.filter(nomina=nomina).select_related("concepto").order_by("concepto__tipo", "id")
    resumen = resumen_nomina(profesor.id, nomina.periodo)
    total_deducciones = nomina.total_impuestos + nomina.total_deducciones
    total_neto = nomina.total_neto
    descuento_asistencia = min(resumen["descuento_asistencia"], nomina.total_deducciones)

    context = {
        "nomina": nomina,
        "profesor": profesor,
        "detalles": detalles,
        "detalle_percepciones": detalles.filter(concepto__tipo="PERCEPCION"),
        "detalle_deducciones": detalles.filter(concepto__tipo="DEDUCCION"),
        "editable": nomina.periodo.estado == "ABIERTO" and nomina.estado not in {"cerrada", "pagada"},
        "total_faltas": resumen["horas_descuento"],
        "descuento_asistencia": descuento_asistencia,
        "periodo_label": f"{nomina.periodo.fecha_inicio:%d} al {nomina.periodo.fecha_fin:%d %B %Y}",
        "preview_total_percepciones": nomina.total_percepciones,
        "preview_total_deducciones": total_deducciones,
        "preview_descuento_faltas": descuento_asistencia,
        "preview_total_neto": total_neto,
        "preview_total_neto_texto": dinero_a_texto(total_neto),
    }
    return render(request, "Contabilidad/nomina_gen.html", context)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def generar_nominas(request):
    try:
        nominas = generar_nominas_periodo()
        notify_role(
            "contabilidad",
            "Nominas generadas",
            f"Se generaron {len(nominas)} nominas del periodo activo.",
            "success",
            "/contabilidad/",
        )
        for nomina in nominas:
            notify_user(
                nomina.profesor.usuario,
                "Nomina disponible",
                "Tu nomina del periodo activo esta disponible.",
                "success",
                "/profesores/?page=recibos",
            )
        messages.success(request, f"Se generaron {len(nominas)} nominas.")
    except Exception as exc:
        messages.error(request, str(exc))
        _notify_error_admin(str(exc))
    return redirect("contabilidad_dashboard")


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def regenerar_nomina(request, nomina_id):
    nomina = get_object_or_404(Nomina.objects.select_related("profesor"), id=nomina_id)
    try:
        nomina = regenerar_nomina_profesor(nomina.profesor_id, nomina.periodo)
        notify_user(
            nomina.profesor.usuario,
            "Nomina actualizada",
            "Tu nomina fue regenerada con la informacion actualizada.",
            "info",
            "/profesores/?page=recibos",
        )
        notify_role(
            "contabilidad",
            "Nomina regenerada",
            f"Se regenero la nomina de {nomina.profesor.usuario.get_full_name()}.",
            "info",
            "/contabilidad/",
        )
        messages.success(request, "Nomina regenerada correctamente.")
        return redirect("detalle_nomina", nomina_id=nomina.id)
    except Exception as exc:
        messages.error(request, str(exc))
        _notify_error_admin(str(exc))
        return redirect("detalle_nomina", nomina_id=nomina.id)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def regenerar_nominas(request):
    try:
        nominas = regenerar_nominas_periodo()
        notify_role(
            "contabilidad",
            "Nominas regeneradas",
            f"Se regeneraron {len(nominas)} nominas del periodo activo.",
            "info",
            "/contabilidad/",
        )
        messages.success(request, f"Se regeneraron {len(nominas)} nominas.")
    except Exception as exc:
        messages.error(request, str(exc))
        _notify_error_admin(str(exc))
    return redirect("contabilidad_dashboard")


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def agregar_concepto(request, nomina_id):
    try:
        nomina = agregar_concepto_nomina(
            nomina_id,
            request.POST.get("concept_type"),
            request.POST.get("concept_name"),
            request.POST.get("concept_amount"),
            request.POST.get("concept_detail"),
        )
        messages.success(request, "Concepto agregado y totales recalculados.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("detalle_nomina", nomina_id=nomina_id)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def eliminar_concepto(request, detalle_id):
    detalle = get_object_or_404(DetalleNomina, id=detalle_id)
    nomina_id = detalle.nomina_id
    try:
        eliminar_concepto_nomina(detalle_id)
        messages.success(request, "Concepto eliminado y totales recalculados.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("detalle_nomina", nomina_id=nomina_id)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def cerrar_nomina(request, nomina_id):
    try:
        nomina = cerrar_nomina_activa(nomina_id)
        messages.success(request, "Nomina cerrada correctamente.")
        return redirect("detalle_nomina", nomina_id=nomina.id)
    except Exception as exc:
        messages.error(request, str(exc))
        return redirect("detalle_nomina", nomina_id=nomina_id)


@require_POST
@login_required
@requiere_rol("contabilidad", "administrador")
def pagar_nomina(request, nomina_id):
    try:
        nomina = marcar_nomina_pagada(nomina_id)
        messages.success(request, f"Nomina de {nomina.profesor.usuario.get_full_name()} marcada como pagada.")
    except Exception as exc:
        messages.error(request, str(exc))

    return redirect("detalle_nomina", nomina_id=nomina_id)


@login_required
@requiere_rol("contabilidad", "administrador")
def vista_previa_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id)
    context = {
        "periodo": periodo,
        "resumen": obtener_resumen_periodo(periodo),
    }
    return render(request, "Contabilidad/vista_previa_periodo.html", context)


@login_required
@requiere_rol("contabilidad", "administrador")
def reporte_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id)
    estado = request.GET.get("estado") or ""
    profesor_id = request.GET.get("profesor") or ""
    nominas = obtener_nominas_periodo(periodo, profesor_id=profesor_id, estado=estado)
    context = {
        "periodo": periodo,
        "nominas": nominas,
        "totales": obtener_totales_periodo(periodo, list(nominas)),
        "resumen": obtener_resumen_periodo(periodo),
        "profesores": Profesor.objects.select_related("usuario").order_by("usuario__nombre"),
        "selected_estado": estado,
        "selected_profesor": profesor_id,
    }
    return render(request, "Contabilidad/reporte_periodo.html", context)


@login_required
def recibo_nomina_pdf(request, nomina_id):
    nomina = get_object_or_404(
        Nomina.objects.select_related("profesor", "profesor__usuario", "profesor__departamento", "periodo"),
        id=nomina_id,
    )
    role = _user_role(request.user)
    if role == "profesor" and nomina.profesor.usuario_id != request.user.id:
        return HttpResponseForbidden("No puedes consultar recibos de otro profesor.")
    if role == "profesor" and nomina.estado != "pagada":
        return HttpResponseForbidden("Tu recibo estara disponible cuando la nomina este pagada.")
    if role not in {"profesor", "contabilidad", "administrador", "admin"}:
        return HttpResponseForbidden("Tu rol no tiene acceso a este recibo.")
    if not puede_generar_recibo(nomina):
        messages.error(request, "Solo se pueden generar recibos PDF de nominas cerradas o pagadas.")
        if role == "profesor":
            return redirect("/profesores/?page=recibos")
        return redirect("detalle_nomina", nomina_id=nomina.id)

    filename = f"recibo_nomina_{nomina.id}.pdf"
    return _pdf_response(
        generar_texto_recibo(nomina),
        filename,
        download=request.GET.get("download") == "1",
    )


@login_required
def recibo_nomina_print(request, nomina_id):
    nomina = get_object_or_404(
        Nomina.objects.select_related("profesor", "profesor__usuario", "profesor__departamento", "periodo"),
        id=nomina_id,
    )
    role = _user_role(request.user)
    if role == "profesor" and nomina.profesor.usuario_id != request.user.id:
        return HttpResponseForbidden("No puedes consultar recibos de otro profesor.")
    if role == "profesor" and nomina.estado != "pagada":
        return HttpResponseForbidden("Tu recibo estara disponible cuando la nomina este pagada.")
    if role not in {"profesor", "contabilidad", "administrador", "admin"}:
        return HttpResponseForbidden("Tu rol no tiene acceso a este recibo.")
    if not puede_generar_recibo(nomina):
        messages.error(request, "Solo se pueden generar recibos de nominas cerradas o pagadas.")
        if role == "profesor":
            return redirect("/profesores/?page=recibos")
        return redirect("detalle_nomina", nomina_id=nomina.id)

    contexto = generar_contexto_recibo(nomina)
    contexto["auto_print"] = request.GET.get("print") == "1"
    contexto["es_profesor"] = role == "profesor"
    contexto["preview_total_deducciones"] = nomina.total_impuestos + nomina.total_deducciones
    contexto["preview_total_neto_texto"] = dinero_a_texto(nomina.total_neto)
    return render(request, "Contabilidad/recibo_nomina_print.html", contexto)


@login_required
@requiere_rol("contabilidad", "administrador")
def reporte_periodo_pdf(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id)
    filename = f"reporte_nomina_periodo_{periodo.id}.pdf"
    return _pdf_response(
        generar_texto_reporte_periodo(periodo, request.user),
        filename,
        download=request.GET.get("download") == "1",
    )


@login_required
@requiere_rol("contabilidad", "administrador")
def reporte_periodo_print(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id)
    context = {
        "periodo": periodo,
        "resumen": obtener_resumen_periodo(periodo),
        "tipo_reporte": "Vista previa" if periodo.estado == "ABIERTO" else "Reporte oficial",
        "fecha_generacion": timezone.localtime(timezone.now()),
        "auto_print": request.GET.get("print") == "1",
    }
    return render(request, "Contabilidad/reporte_periodo_print.html", context)
