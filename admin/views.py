from datetime import timedelta

from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.timesince import timesince

from core.models import BitacoraAuditoria, Notificacion, Plantel
from Profesores.models import Profesor
from users.models import Departamento, Rol, RolPermiso, Usuario


def dashboard(request):
    now = timezone.localtime()
    profesores_qs = Profesor.objects.select_related(
        "usuario", "departamento", "departamento__plantel"
    ).prefetch_related("planteles")
    empleados_total = profesores_qs.count()
    empleados_activos = profesores_qs.filter(estado_laboral="ACTIVO").count()
    empleados_bajas = max(0, empleados_total - empleados_activos)
    empleados_ultimos_30 = profesores_qs.filter(
        usuario__date_joined__gte=now - timedelta(days=30)
    ).count()

    planteles_qs = Plantel.objects.all()
    planteles_total = planteles_qs.count()
    planteles_label = ", ".join(list(planteles_qs.values_list("nombre", flat=True)[:3]))

    departamentos_qs = Departamento.objects.select_related("plantel")
    departamentos_total = departamentos_qs.count()
    departamentos_activos = departamentos_qs.filter(activo=True).count()
    departamentos_label = (
        "Todos activos"
        if departamentos_total and departamentos_activos == departamentos_total
        else f"{departamentos_activos} activos"
    )

    usuarios_total = Usuario.objects.count()
    usuarios_roles_label = f"{Usuario.objects.values('rol_id').distinct().count()} roles"

    notificaciones_count = Notificacion.objects.filter(
        usuario=request.user, leida=False
    ).count()

    modelo_to_modulo = {
        "SolicitudAprobacion": ("Solicitudes", "pill-blue"),
        "Usuario": ("Usuarios", "pill-yellow"),
        "Rol": ("Usuarios", "pill-yellow"),
        "Plantel": ("Planteles", "pill-blue"),
        "Departamento": ("Departamentos", "pill-blue"),
        "BitacoraAuditoria": ("Sistema", "pill-gray"),
    }

    recent_activity = []
    for item in (
        BitacoraAuditoria.objects.select_related("usuario")
        .order_by("-fecha")[:6]
    ):
        modulo, modulo_clase = modelo_to_modulo.get(
            item.modelo, (item.modelo, "pill-gray")
        )
        recent_activity.append(
            {
                "cuando": f"Hace {timesince(item.fecha).split(',')[0]}",
                "usuario": f"{item.usuario.nombre} {item.usuario.apellido}",
                "accion": item.accion,
                "modulo": modulo,
                "modulo_clase": modulo_clase,
            }
        )

    roles = list(Rol.objects.all().order_by("nombre"))
    permisos_por_rol = {
        role.id: RolPermiso.objects.filter(rol=role).count() for role in roles
    }
    usuarios_por_rol = {
        role.id: Usuario.objects.filter(rol_id=role).count() for role in roles
    }

    permisos_resumen = [
        {
            "modulo": "Permisos asignados",
            "valores": [permisos_por_rol.get(r.id, 0) for r in roles],
        },
        {
            "modulo": "Usuarios con rol",
            "valores": [usuarios_por_rol.get(r.id, 0) for r in roles],
        },
    ]

    usuarios_qs = Usuario.objects.select_related("rol_id").order_by("-last_login")[:20]
    usuarios_ids = list(usuarios_qs.values_list("id", flat=True))

    profes_by_user = {
        p.usuario_id: p
        for p in Profesor.objects.filter(usuario_id__in=usuarios_ids)
        .select_related("departamento", "departamento__plantel")
        .prefetch_related("planteles")
    }
    dept_by_jefe = {
        d.jefe_id: d
        for d in Departamento.objects.filter(jefe_id__in=usuarios_ids)
        .select_related("plantel")
    }

    rol_style = {
        "administrador": ("Admin", "chip-admin", "🛡️", "admin"),
        "admin": ("Admin", "chip-admin", "🛡️", "admin"),
        "jefatura": ("Jefatura", "chip-jefe", "👔", "jefatura"),
        "contabilidad": ("Contabilidad", "chip-conta", "💼", "contabilidad"),
        "profesor": ("Profesor", "chip-prof", "📚", "profesor"),
    }

    usuarios = []
    for u in usuarios_qs:
        rol_nombre = (u.rol_id.nombre if u.rol_id else "Sin rol").lower()
        rol_label, rol_clase, rol_icono, rol_key = rol_style.get(
            rol_nombre, ("Sin rol", "chip-prof", "👤", "sin-rol")
        )

        plantel_nombre = ""
        plantel_key = ""
        if rol_key == "admin":
            plantel_nombre = "Todos"
            plantel_key = "todos"
        else:
            profesor = profes_by_user.get(u.id)
            if profesor and profesor.planteles.exists():
                plantel = profesor.planteles.first()
                plantel_nombre = plantel.nombre
                plantel_key = plantel.nombre.lower().replace(" ", "-")
            else:
                depto = dept_by_jefe.get(u.id)
                if depto:
                    plantel_nombre = depto.plantel.nombre
                    plantel_key = depto.plantel.nombre.lower().replace(" ", "-")

        plantel_clase = "pill-gray" if plantel_nombre == "Todos" else "pill-blue"
        ultimo_acceso = (
            f"Hace {timesince(u.last_login).split(',')[0]}"
            if u.last_login
            else "Nunca"
        )
        estado_label = "Activo" if u.is_active else "Inactivo"
        estado_clase = "pill-green" if u.is_active else "pill-yellow"

        usuarios.append(
            {
                "username": u.email,
                "nombre": f"{u.nombre} {u.apellido}",
                "rol_label": rol_label,
                "rol_clase": rol_clase,
                "rol_icono": rol_icono,
                "plantel": plantel_nombre or "Sin plantel",
                "plantel_clase": plantel_clase,
                "ultimo_acceso": ultimo_acceso,
                "estado_label": estado_label,
                "estado_clase": estado_clase,
                "rol": rol_key,
                "plantel_key": plantel_key or "sin-plantel",
            }
        )

    empleados_data = []
    for p in profesores_qs:
        plantel_nombre = (
            p.planteles.first().nombre if p.planteles.exists() else "Sin plantel"
        )
        empleados_data.append(
            {
                "id": p.id,
                "nombre": f"{p.usuario.nombre} {p.usuario.apellido}",
                "plantel": plantel_nombre,
                "dept": p.departamento.nombre,
                "puesto": p.tipo_contrato,
                "salario": f"${p.costo_por_hora:.2f}/h",
                "estado": "activo" if p.estado_laboral == "ACTIVO" else "baja",
            }
        )

    depts_by_plantel = {}
    for dept in departamentos_qs:
        key = dept.plantel_id
        depts_by_plantel.setdefault(key, []).append(dept.nombre)

    dept_prof_counts = (
        Profesor.objects.values("departamento_id")
        .annotate(total=Count("id"), activos=Count("id", filter=Q(estado_laboral="ACTIVO")))
    )
    dept_counts = {d["departamento_id"]: d for d in dept_prof_counts}

    color_cycle = ["bar-blue", "bar-teal", "bar-orange", "bar-red"]
    planteles_data = []
    for idx, plantel in enumerate(planteles_qs):
        jefe_nombre = "Sin asignar"
        jefe_depto = (
            departamentos_qs.filter(plantel=plantel).select_related("jefe").first()
        )
        if jefe_depto and jefe_depto.jefe:
            jefe_nombre = f"{jefe_depto.jefe.nombre} {jefe_depto.jefe.apellido}"

        depts_list = []
        for dept in departamentos_qs.filter(plantel=plantel):
            counts = dept_counts.get(dept.id, {"total": 0, "activos": 0})
            total = counts.get("total", 0) or 0
            activos = counts.get("activos", 0) or 0
            prog = int((activos / total) * 100) if total else 0
            depts_list.append(
                {
                    "nombre": dept.nombre,
                    "empleados": total,
                    "prog": prog,
                }
            )

        planteles_data.append(
            {
                "id": plantel.id,
                "nombre": plantel.nombre,
                "icon": plantel.nombre[:1].upper(),
                "color": color_cycle[idx % len(color_cycle)],
                "empleados": profesores_qs.filter(planteles=plantel).count(),
                "jefe": jefe_nombre,
                "dir": plantel.direccion,
                "depts": depts_list,
            }
        )

    context = {
        "fecha_actual": now.strftime("%B %Y").capitalize(),
        "notificaciones_count": notificaciones_count,
        "stats": {
            "empleados_total": empleados_total,
            "empleados_activos": empleados_activos,
            "empleados_bajas": empleados_bajas,
            "empleados_trend": f"+{empleados_ultimos_30}" if empleados_ultimos_30 else "—",
            "planteles_total": planteles_total,
            "planteles_label": planteles_label,
            "departamentos_total": departamentos_total,
            "departamentos_label": departamentos_label,
            "usuarios_total": usuarios_total,
            "usuarios_roles_label": usuarios_roles_label,
        },
        "recent_activity": recent_activity,
        "usuarios": usuarios,
        "roles_permisos": roles,
        "permisos_resumen": permisos_resumen,
        "empleados_data": empleados_data,
        "depts_by_plantel": depts_by_plantel,
        "planteles_data": planteles_data,
    }
    return render(request, "admin/dashboard.html", context)
