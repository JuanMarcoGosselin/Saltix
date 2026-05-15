from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timesince import timesince
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

from .models import Notificacion
from .utils import mark_all_as_read, mark_as_read


def _safe_next(request):
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return "notifications:list"


@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        archivada=False,
    ).order_by("-creada_en", "-id")
    return render(
        request,
        "Notifications/lista.html",
        {"notificaciones": notificaciones},
    )


@require_GET
@login_required
def estado_notificaciones(request):
    qs = Notificacion.objects.filter(usuario=request.user, archivada=False)
    latest = qs.order_by("-creada_en", "-id")[:5]
    return JsonResponse({
        "ok": True,
        "unread_count": qs.filter(leida=False).count(),
        "notifications": [
            {
                "id": notificacion.id,
                "title": notificacion.titulo,
                "message": notificacion.mensaje,
                "type": notificacion.tipo,
                "url": notificacion.url or "",
                "mark_read_url": reverse("notifications:mark_read", args=[notificacion.id]),
                "is_read": notificacion.leida,
                "created": notificacion.creada_en.strftime("%d/%m/%Y %H:%M"),
                "when": f"Hace {timesince(notificacion.creada_en).split(',')[0]}",
            }
            for notificacion in latest
        ],
    })


@require_POST
@login_required
def marcar_leida(request, notificacion_id):
    notificacion = get_object_or_404(
        Notificacion,
        id=notificacion_id,
        usuario=request.user,
    )
    mark_as_read(notificacion, request.user)
    return redirect(_safe_next(request))


@require_POST
@login_required
def marcar_todas_leidas(request):
    mark_all_as_read(request.user)
    return redirect(_safe_next(request))
