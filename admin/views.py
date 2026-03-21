from datetime import date, timedelta
import re
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.timesince import timesince
from django.urls import reverse

from core.models import BitacoraAuditoria, Notificacion, Plantel
from Profesores.models import Profesor, Horario, TransferenciaDepartamento
from users.models import Departamento, Permiso, Rol, RolPermiso, Usuario

from core.decorators import requiere_rol, requiere_permiso


@requiere_rol("administrador")
@requiere_permiso("auditoria.ver_bitacora")
def dashboard(request):
    now = timezone.localtime()
    profesores_qs = Profesor.objects.select_related(
        "usuario"
    ).prefetch_related("planteles", "departamentos")
    empleados_total = profesores_qs.count()
    empleados_activos = profesores_qs.filter(estado_laboral="ACTIVO").count()
    empleados_bajas = max(0, empleados_total - empleados_activos)
    empleados_ultimos_30 = profesores_qs.filter(
        usuario__date_joined__gte=now - timedelta(days=30)
    ).count()

    planteles_qs = Plantel.objects.all()
    planteles_total = planteles_qs.count()
    planteles_label = ", ".join(list(planteles_qs.values_list("nombre", flat=True)[:3]))
    if not planteles_label:
        planteles_label = "Sin planteles"

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

    notificaciones_qs = Notificacion.objects.filter(
        usuario=request.user,
        fecha__gte=now - timedelta(days=7),
        leida=False,
    ).order_by("-fecha")
    notificaciones_count = notificaciones_qs.count()

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
    permisos_catalogo = list(Permiso.objects.all().order_by("codigo"))
    rol_perm_map = {role.id: set() for role in roles}
    for rp in RolPermiso.objects.filter(rol__in=roles, permiso__in=permisos_catalogo):
        rol_perm_map.setdefault(rp.rol_id, set()).add(rp.permiso_id)
    roles_detalle = [
        {
            "id": role.id,
            "nombre": role.nombre,
            "perm_ids": sorted(list(rol_perm_map.get(role.id, set()))),
            "usuarios": usuarios_por_rol.get(role.id, 0),
            "permisos": permisos_por_rol.get(role.id, 0),
        }
        for role in roles
    ]

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
        .select_related("usuario")
        .prefetch_related("planteles", "departamentos")
    }
    horarios_by_user = {}
    for h in Horario.objects.filter(profesor__usuario_id__in=usuarios_ids, activo=True).select_related("profesor"):
        horarios_by_user.setdefault(h.profesor.usuario_id, []).append(
            {
                "dia": h.dia_semana,
                "inicio": h.hora_inicio.strftime("%H:%M"),
                "fin": h.hora_fin.strftime("%H:%M"),
                "aula": h.aula,
            }
        )
    dept_by_jefe = {
        d.jefe_id: d
        for d in Departamento.objects.filter(jefe_id__in=usuarios_ids)
        .select_related("plantel")
    }
    dept_by_jefe_all = {
        d.jefe_id: d
        for d in Departamento.objects.select_related("plantel", "jefe")
    }
    rol_style = {
        "administrador": ("Admin", "chip-admin", "Admin", "administrador"),
        "admin": ("Admin", "chip-admin", "Admin", "administrador"),
        "jefatura": ("Jefatura", "chip-jefe", "Jefatura", "jefatura"),
        "contabilidad": ("Contabilidad", "chip-conta", "Contabilidad", "contabilidad"),
        "profesor": ("Profesor", "chip-prof", "Profesor", "profesor"),
    }
    usuarios = []
    for u in usuarios_qs:
        rol_nombre = (u.rol_id.nombre if u.rol_id else "Sin rol").lower()
        rol_label, rol_clase, rol_icono, rol_key = rol_style.get(
            rol_nombre, ("Sin rol", "chip-prof", "Usuario", "sin-rol")
        )

        plantel_nombre = ""
        plantel_key = ""
        plantel_ids = []
        depto_nombres = []
        depto_ids = []
        jef_plantel_id = ""
        jef_depto_id = ""
        prof_data = {}
        if rol_key == "administrador":
            plantel_nombre = "Todos"
            plantel_key = "todos"
        elif rol_key == "contabilidad":
            plantel_nombre = "Todos"
            plantel_key = "todos"
        else:
            profesor = profes_by_user.get(u.id)
            if profesor:
                if profesor.planteles.exists():
                    plantel_ids = [str(p.id) for p in profesor.planteles.all()]
                    plantel_nombres = [p.nombre for p in profesor.planteles.all()]
                    plantel_nombre = ", ".join(plantel_nombres)
                    plantel_key = plantel_nombres[0].lower().replace(" ", "-")
                elif profesor.departamentos.exists():
                    dept_planteles = {d.plantel for d in profesor.departamentos.select_related("plantel")}
                    plantel_ids = [str(p.id) for p in dept_planteles]
                    plantel_nombres = [p.nombre for p in dept_planteles]
                    plantel_nombre = ", ".join(plantel_nombres)
                    if plantel_nombres:
                        plantel_key = plantel_nombres[0].lower().replace(" ", "-")
                depto_ids = [str(d.id) for d in profesor.departamentos.all()]
                depto_nombres = [d.nombre for d in profesor.departamentos.all()]
                prof_data = {
                    "rfc": profesor.rfc,
                    "curp": profesor.curp,
                    "telefono": profesor.telefono,
                    "direccion": profesor.direccion,
                    "fecha_ingreso": profesor.fecha_ingreso.isoformat(),
                    "tipo_contrato": profesor.tipo_contrato,
                    "salario": f"{profesor.costo_por_hora:.2f}",
                }
            else:
                depto = dept_by_jefe.get(u.id)
                if depto:
                    plantel_nombre = depto.plantel.nombre
                    plantel_key = depto.plantel.nombre.lower().replace(" ", "-")
                    plantel_ids = [str(depto.plantel_id)]
                    depto_nombres = [depto.nombre]
                    depto_ids = [str(depto.id)]
                    jef_plantel_id = str(depto.plantel_id)
                    jef_depto_id = str(depto.id)

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
                "id": u.id,
                "email": u.email,
                "nombre": u.nombre,
                "apellido": u.apellido,
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
                "plantel_ids": plantel_ids,
                "departamento_nombres": depto_nombres,
                "departamento_ids": depto_ids,
                "jefatura_plantel_id": jef_plantel_id,
                "jefatura_depto_id": jef_depto_id,
                "profesor": prof_data,
            }
        )

    rol_order = {
        "jefatura": 1,
        "profesor": 2,
        "contabilidad": 3,
        "administrador": 4,
        "admin": 4,
    }
    usuarios.sort(key=lambda u: (rol_order.get(u.get("rol"), 99), u.get("nombre") or "", u.get("apellido") or ""))

    empleados_data = []
    for p in profesores_qs:
        if p.planteles.exists():
            plantel_nombre = ", ".join([pl.nombre for pl in p.planteles.all()])
        else:
            plantel_nombre = "Sin plantel"
        dept_names = [d.nombre for d in p.departamentos.all()]
        dept_label = ", ".join(dept_names) if dept_names else "Sin departamento"
        empleados_data.append(
            {
                "id": p.id,
                "nombre": f"{p.usuario.nombre} {p.usuario.apellido}",
                "plantel": plantel_nombre,
                "dept": dept_label,
                "puesto": p.tipo_contrato,
                "salario": f"${p.costo_por_hora:.2f}/h",
                "estado": "activo" if p.estado_laboral == "ACTIVO" else "baja",
            }
        )

    depts_by_plantel = {}
    for dept in departamentos_qs:
        key = str(dept.plantel_id)
        depts_by_plantel.setdefault(key, []).append(
            {
                "id": dept.id,
                "nombre": dept.nombre,
                "plantel_id": dept.plantel_id,
                "plantel_nombre": dept.plantel.nombre,
            }
        )

    dept_prof_counts = (
        Profesor.objects.values("departamentos")
        .annotate(total=Count("id"), activos=Count("id", filter=Q(estado_laboral="ACTIVO")))
    )
    dept_counts = {d["departamentos"]: d for d in dept_prof_counts if d["departamentos"]}

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
                    "id": dept.id,
                    "nombre": dept.nombre,
                    "descripcion": dept.descripcion,
                    "empleados": total,
                    "prog": prog,
                    "activo": dept.activo,
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
                "activo": plantel.activo,
                "depts": depts_list,
            }
        )

    dias = [
        ('LUN','Lunes'),
        ('MAR','Martes'),
        ('MIE','Miercoles'),
        ('JUE','Jueves'),
        ('VIE','Viernes'),
        ('SAB','Sabado')
    ]
    horas = list(range(6, 24))

    jefes_data = []
    for u in Usuario.objects.select_related("rol_id").filter(
        rol_id__nombre__iexact="jefatura"
    ):
        depto = dept_by_jefe_all.get(u.id)
        jefes_data.append(
            {
                "id": u.id,
                "nombre": f"{u.nombre} {u.apellido}",
                "dept_id": depto.id if depto else None,
                "plantel_id": depto.plantel_id if depto else None,
            }
        )

    context = {
        "fecha_actual": now.strftime("%B %Y").capitalize(),
        "notificaciones_count": notificaciones_count,
        "notificaciones": [
            {
                "id": n.id,
                "mensaje": n.mensaje,
                "tipo": n.tipo,
                "cuando": f"Hace {timesince(n.fecha).split(',')[0]}",
            }
            for n in notificaciones_qs[:20]
        ],
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
        "horarios_by_user": horarios_by_user,
        "roles_permisos": roles,
        "roles_detalle": roles_detalle,
        "permisos_catalogo": permisos_catalogo,
        "permisos_resumen": permisos_resumen,
        "empleados_data": empleados_data,
        "depts_by_plantel": depts_by_plantel,
        "planteles_data": planteles_data,
        "dias": dias,
        "horas": horas,
        "jefes_data": jefes_data,
    }
    return render(request, "admin/dashboard.html", context)


def _redirect_with_message(request, ok=None, error=None):
    base = reverse("admin_dashboard")
    msg = ok or error
    if msg and getattr(request, "user", None) and request.user.is_authenticated:
        tipo = "SISTEMA" if ok else "INCIDENCIA"
        Notificacion.objects.create(usuario=request.user, tipo=tipo, mensaje=msg, leida=False)
    return base


@requiere_rol("administrador")
@requiere_permiso("users.manage_users")
def create_user(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    email = (request.POST.get("email") or "").strip().lower()
    nombre = (request.POST.get("nombre") or "").strip()
    apellido = (request.POST.get("apellido") or "").strip()
    rol_nombre = (request.POST.get("rol") or "").strip()
    password = request.POST.get("password") or ""
    password2 = request.POST.get("password2") or ""

    if not email or not nombre or not apellido or not rol_nombre:
        return redirect(_redirect_with_message(request, error="Completa email, nombre, apellido y rol."))

    if not password:
        return redirect(_redirect_with_message(request, error="La contrasena es obligatoria."))
    if password != password2:
        return redirect(_redirect_with_message(request, error="Las contraseñas no coinciden."))

    if Usuario.objects.filter(email=email).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un usuario con ese email."))

    rol = Rol.objects.filter(nombre__iexact=rol_nombre).first()
    if not rol:
        return redirect(_redirect_with_message(request, error="Rol no valido."))

    user = Usuario.objects.create_user(
        email=email,
        password=password,
        nombre=nombre,
        apellido=apellido,
        rol_id=rol,
        is_active=True,
    )

    rol_key = rol.nombre.lower()
    if rol_key == "profesor":
        prof_err = _upsert_profesor_from_request(request, user, is_new=True)
        if prof_err:
            user.delete()
            return redirect(_redirect_with_message(request, error=prof_err))
    elif rol_key == "jefatura":
        jefe_err = _assign_jefatura_departamento(request, user)
        if jefe_err:
            user.delete()
            return redirect(_redirect_with_message(request, error=jefe_err))

    return redirect(_redirect_with_message(request, ok="Usuario creado."))


@requiere_rol("administrador")
@requiere_permiso("users.manage_users")
def update_user(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    user_id = request.POST.get("user_id")
    if not user_id:
        return redirect(_redirect_with_message(request, error="Usuario no encontrado."))

    user = Usuario.objects.filter(id=user_id).select_related("rol_id").first()
    if not user:
        return redirect(_redirect_with_message(request, error="Usuario no encontrado."))

    email = (request.POST.get("email") or "").strip().lower()
    nombre = (request.POST.get("nombre") or "").strip()
    apellido = (request.POST.get("apellido") or "").strip()
    rol_nombre = (request.POST.get("rol") or "").strip()
    password = request.POST.get("password") or ""
    password2 = request.POST.get("password2") or ""

    if not email or not nombre or not apellido or not rol_nombre:
        return redirect(_redirect_with_message(request, error="Completa email, nombre, apellido y rol."))

    if password and password != password2:
        return redirect(_redirect_with_message(request, error="Las contraseñas no coinciden."))

    if Usuario.objects.exclude(id=user.id).filter(email=email).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un usuario con ese email."))

    rol = Rol.objects.filter(nombre__iexact=rol_nombre).first()
    if not rol:
        return redirect(_redirect_with_message(request, error="Rol no valido."))

    user.email = email
    user.nombre = nombre
    user.apellido = apellido
    user.rol_id = rol
    if password:
        user.set_password(password)
    user.save()

    rol_key = rol.nombre.lower()
    if rol_key == "profesor":
        prof_err = _upsert_profesor_from_request(request, user, is_new=False)
        if prof_err:
            return redirect(_redirect_with_message(request, error=prof_err))
        _clear_jefatura_if_needed(request, user)
    elif rol_key == "jefatura":
        jefe_err = _assign_jefatura_departamento(request, user)
        if jefe_err:
            return redirect(_redirect_with_message(request, error=jefe_err))
    else:
        _clear_jefatura_if_needed(request, user)

    return redirect(_redirect_with_message(request, ok="Usuario actualizado."))


@requiere_rol("administrador")
@requiere_permiso("users.manage_roles")
def update_role_permissions(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    roles = list(Rol.objects.all())
    permisos = list(Permiso.objects.all())
    permisos_ids = {p.id for p in permisos}

    for role in roles:
        selected_ids = set()
        for val in request.POST.getlist(f"perms_{role.id}"):
            try:
                selected_ids.add(int(val))
            except (TypeError, ValueError):
                continue
        selected_ids &= permisos_ids

        existing_ids = set(
            RolPermiso.objects.filter(rol=role, permiso_id__in=permisos_ids)
            .values_list("permiso_id", flat=True)
        )

        to_add = selected_ids - existing_ids
        if to_add:
            RolPermiso.objects.bulk_create(
                [RolPermiso(rol=role, permiso_id=pid) for pid in to_add],
                ignore_conflicts=True,
            )

        to_remove = existing_ids - selected_ids
        if to_remove:
            RolPermiso.objects.filter(rol=role, permiso_id__in=to_remove).delete()

    return redirect(_redirect_with_message(request, ok="Permisos por rol actualizados."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_plantel")
def create_plantel(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    nombre = (request.POST.get("plantel_nombre") or "").strip()
    direccion = (request.POST.get("plantel_direccion") or "").strip()
    activo = request.POST.get("plantel_activo") == "on"
    departamentos_raw = (request.POST.get("departamentos_csv") or "").strip()

    if not nombre or not direccion:
        return redirect(_redirect_with_message(request, error="Nombre y direccion del plantel son obligatorios."))

    if Plantel.objects.filter(nombre__iexact=nombre).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un plantel con ese nombre."))

    departamentos = [
        d.strip() for d in departamentos_raw.replace(";", ",").split(",") if d.strip()
    ]
    if not departamentos:
        return redirect(_redirect_with_message(request, error="Agrega al menos un departamento."))

    plantel = Plantel.objects.create(nombre=nombre, direccion=direccion, activo=activo)
    for dept in departamentos:
        Departamento.objects.create(
            nombre=dept,
            descripcion=dept,
            jefe=request.user,
            plantel=plantel,
            activo=True,
        )

    return redirect(_redirect_with_message(request, ok="Plantel creado."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_plantel")
def update_plantel(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    plantel_id = request.POST.get("plantel_id")
    if not plantel_id:
        return redirect(_redirect_with_message(request, error="Plantel no encontrado."))

    plantel = Plantel.objects.filter(id=plantel_id).first()
    if not plantel:
        return redirect(_redirect_with_message(request, error="Plantel no encontrado."))

    nombre = (request.POST.get("plantel_nombre") or "").strip()
    direccion = (request.POST.get("plantel_direccion") or "").strip()
    activo = request.POST.get("plantel_activo") == "on"

    if not nombre or not direccion:
        return redirect(_redirect_with_message(request, error="Nombre y direccion del plantel son obligatorios."))

    if Plantel.objects.exclude(id=plantel.id).filter(nombre__iexact=nombre).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un plantel con ese nombre."))

    plantel.nombre = nombre
    plantel.direccion = direccion
    plantel.activo = activo
    plantel.save()

    return redirect(_redirect_with_message(request, ok="Plantel actualizado."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_plantel")
def delete_plantel(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    plantel_id = request.POST.get("plantel_id")
    if not plantel_id:
        return redirect(_redirect_with_message(request, error="Plantel no encontrado."))

    plantel = Plantel.objects.filter(id=plantel_id).first()
    if not plantel:
        return redirect(_redirect_with_message(request, error="Plantel no encontrado."))

    if plantel.profesores.exists():
        return redirect(_redirect_with_message(request, error="No puedes eliminar el plantel porque tiene profesores asignados."))

    departamentos = list(Departamento.objects.filter(plantel=plantel))
    for depto in departamentos:
        if depto.profesores.exists():
            return redirect(_redirect_with_message(request, error=f"No puedes eliminar el plantel porque el departamento \"{depto.nombre}\" tiene profesores asignados."))
        if TransferenciaDepartamento.objects.filter(
            Q(departamento_origen=depto) | Q(departamento_destino=depto)
        ).exists():
            return redirect(_redirect_with_message(request, error=f"No puedes eliminar el plantel porque el departamento \"{depto.nombre}\" tiene historial de transferencias."))

    for depto in departamentos:
        depto.delete()

    plantel.delete()
    return redirect(_redirect_with_message(request, ok="Plantel eliminado."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_departamento")
def create_departamento(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    plantel_id = request.POST.get("dept_plantel_id")
    nombre = (request.POST.get("dept_nombre") or "").strip()
    descripcion = (request.POST.get("dept_descripcion") or "").strip()
    activo = request.POST.get("dept_activo") == "on"
    jefe_id = (request.POST.get("dept_jefe_id") or "").strip()

    if not plantel_id or not nombre:
        return redirect(_redirect_with_message(request, error="Plantel y nombre del departamento son obligatorios."))

    plantel = Plantel.objects.filter(id=plantel_id).first()
    if not plantel:
        return redirect(_redirect_with_message(request, error="Plantel no encontrado."))

    if Departamento.objects.filter(plantel=plantel, nombre__iexact=nombre).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un departamento con ese nombre en el plantel."))

    jefe = None
    if jefe_id:
        jefe = Usuario.objects.select_related("rol_id").filter(id=jefe_id).first()
        if not jefe or not jefe.rol_id or jefe.rol_id.nombre.lower() != "jefatura":
            return redirect(_redirect_with_message(request, error="Jefe invalido para departamento."))
        if Departamento.objects.filter(jefe=jefe).exists():
            return redirect(_redirect_with_message(request, error="Ese jefe ya esta asignado a un plantel."))

    Departamento.objects.create(
        nombre=nombre,
        descripcion=descripcion or nombre,
        jefe=jefe or request.user,
        plantel=plantel,
        activo=activo,
    )

    return redirect(_redirect_with_message(request, ok="Departamento creado."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_departamento")
def update_departamento(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    dept_id = request.POST.get("dept_id")
    if not dept_id:
        return redirect(_redirect_with_message(request, error="Departamento no encontrado."))

    depto = Departamento.objects.select_related("plantel").filter(id=dept_id).first()
    if not depto:
        return redirect(_redirect_with_message(request, error="Departamento no encontrado."))

    nombre = (request.POST.get("dept_nombre") or "").strip()
    descripcion = (request.POST.get("dept_descripcion") or "").strip()
    activo = request.POST.get("dept_activo") == "on"
    jefe_id = (request.POST.get("dept_jefe_id") or "").strip()

    if not nombre:
        return redirect(_redirect_with_message(request, error="Nombre del departamento es obligatorio."))

    if Departamento.objects.filter(plantel=depto.plantel, nombre__iexact=nombre).exclude(id=depto.id).exists():
        return redirect(_redirect_with_message(request, error="Ya existe un departamento con ese nombre en el plantel."))

    jefe = None
    if jefe_id:
        jefe = Usuario.objects.select_related("rol_id").filter(id=jefe_id).first()
        if not jefe or not jefe.rol_id or jefe.rol_id.nombre.lower() != "jefatura":
            return redirect(_redirect_with_message(request, error="Jefe invalido para departamento."))
        if Departamento.objects.filter(jefe=jefe).exclude(id=depto.id).exists():
            return redirect(_redirect_with_message(request, error="Ese jefe ya esta asignado a un plantel."))
    else:
        jefe = request.user

    depto.nombre = nombre
    depto.descripcion = descripcion or nombre
    depto.activo = activo
    if jefe:
        depto.jefe = jefe
    depto.save()

    return redirect(_redirect_with_message(request, ok="Departamento actualizado."))


@requiere_rol("administrador")
@requiere_permiso("admin.manage_departamento")
def delete_departamento(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    dept_id = request.POST.get("dept_id")
    if not dept_id:
        return redirect(_redirect_with_message(request, error="Departamento no encontrado."))

    depto = Departamento.objects.select_related("plantel").filter(id=dept_id).first()
    if not depto:
        return redirect(_redirect_with_message(request, error="Departamento no encontrado."))

    if depto.profesores.exists():
        return redirect(_redirect_with_message(request, error="No puedes eliminar el departamento porque tiene profesores asignados."))

    if TransferenciaDepartamento.objects.filter(
        Q(departamento_origen=depto) | Q(departamento_destino=depto)
    ).exists():
        return redirect(_redirect_with_message(request, error="No puedes eliminar el departamento porque tiene historial de transferencias."))

    depto.delete()
    return redirect(_redirect_with_message(request, ok="Departamento eliminado."))


@requiere_rol("administrador")
@requiere_permiso("notificaciones.manage_notificacion")
def marcar_notificacion_leida(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    notif_id = (request.POST.get("notif_id") or "").strip()
    if not notif_id:
        return redirect("admin_dashboard")

    Notificacion.objects.filter(id=notif_id, usuario=request.user).update(leida=True)
    return redirect("admin_dashboard")


@requiere_rol("administrador")
@requiere_permiso("notificaciones.manage_notificacion")
def marcar_notificaciones_leidas(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    now = timezone.localtime()
    Notificacion.objects.filter(
        usuario=request.user,
        fecha__gte=now - timedelta(days=7),
        leida=False,
    ).update(leida=True)
    return redirect("admin_dashboard")


def _upsert_profesor_from_request(request, user, is_new):
    rfc = (request.POST.get("rfc") or "").strip()
    curp = (request.POST.get("curp") or "").strip()
    telefono = (request.POST.get("telefono") or "").strip()
    direccion = (request.POST.get("direccion") or "").strip()
    fecha_ingreso = (request.POST.get("fecha_ingreso") or "").strip()
    tipo_contrato = (request.POST.get("tipo_contrato") or "").strip()
    dept_ids = request.POST.getlist("departamentos")
    plantel_ids = request.POST.getlist("planteles")
    salario = (request.POST.get("salario") or "").strip()

    if not all([rfc, curp, telefono, direccion, fecha_ingreso, tipo_contrato]):
        return "Completa todos los campos de profesor."

    if not plantel_ids:
        return "Selecciona al menos un plantel para profesor."

    if not dept_ids:
        return "Selecciona al menos un departamento para profesor."

    if not re.match(r"^\d+(\.\d{2})?$", salario):
        return "Salario invalido. Usa formato 0000.00."
    try:
        costo_por_hora = Decimal(salario)
    except (InvalidOperation, TypeError):
        return "Salario invalido. Usa formato 0000.00."

    try:
        fecha_ingreso_dt = date.fromisoformat(fecha_ingreso)
    except ValueError:
        return "Fecha de ingreso invalida."

    planteles = list(Plantel.objects.filter(id__in=plantel_ids))
    if len(planteles) != len(plantel_ids):
        return "Plantel invalido."

    departamentos = list(Departamento.objects.filter(id__in=dept_ids).select_related("plantel"))
    if len(departamentos) != len(dept_ids):
        return "Departamento invalido."

    plantel_id_set = set([p.id for p in planteles])
    for depto in departamentos:
        if depto.plantel_id not in plantel_id_set:
            return "Todos los departamentos deben pertenecer a los planteles seleccionados."

    profesor, _ = Profesor.objects.get_or_create(usuario=user, defaults={
        "rfc": rfc,
        "curp": curp,
        "telefono": telefono,
        "direccion": direccion,
        "fecha_ingreso": fecha_ingreso_dt,
        "estado_laboral": "ACTIVO",
        "costo_por_hora": costo_por_hora,
        "tipo_contrato": tipo_contrato,
    })

    profesor.rfc = rfc
    profesor.curp = curp
    profesor.telefono = telefono
    profesor.direccion = direccion
    profesor.fecha_ingreso = fecha_ingreso_dt
    profesor.costo_por_hora = costo_por_hora
    profesor.tipo_contrato = tipo_contrato
    profesor.save()
    profesor.planteles.set(planteles)
    profesor.departamentos.set(departamentos)

    horario_error = _update_horarios(request, profesor)
    if horario_error:
        return horario_error
    return None


def _update_horarios(request, profesor):
    dias = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB"]
    any_data = False
    entries = []

    for dia in dias:
        inicios = request.POST.getlist(f"horario_{dia}_inicio[]")
        fines = request.POST.getlist(f"horario_{dia}_fin[]")
        aulas = request.POST.getlist(f"horario_{dia}_aula[]")
        clases = request.POST.getlist(f"horario_{dia}_clase_val[]")

        max_len = max(len(inicios), len(fines), len(aulas), len(clases))
        for i in range(max_len):
            inicio = (inicios[i] if i < len(inicios) else "").strip()
            fin = (fines[i] if i < len(fines) else "").strip()
            aula = (aulas[i] if i < len(aulas) else "").strip()
            clase_val = (clases[i] if i < len(clases) else "0").strip()
            enabled = clase_val == "1"

            if enabled or inicio or fin or aula:
                any_data = True

            if enabled and (not inicio or not fin):
                return f"Completa horario de {dia} (inicio y fin)."

            if enabled and inicio and fin:
                entries.append(
                    {
                        "dia_semana": dia,
                        "hora_inicio": inicio,
                        "hora_fin": fin,
                        "aula": aula,
                        "es_hora_clase": True,
                    }
                )

    if not any_data:
        return None

    if any_data and not entries:
        return "Selecciona al menos un bloque con horario de clase."

    profesor.horario_set.update(activo=False)

    for item in entries:
        defaults = {
            "aula": item.get("aula", ""),
            "es_hora_clase": bool(item.get("es_hora_clase", True)),
            "activo": True,
        }
        horario, created = Horario.objects.get_or_create(
            profesor=profesor,
            dia_semana=item["dia_semana"],
            hora_inicio=item["hora_inicio"],
            hora_fin=item["hora_fin"],
            defaults=defaults,
        )
        if not created:
            changed = False
            for field, value in defaults.items():
                if getattr(horario, field) != value:
                    setattr(horario, field, value)
                    changed = True
            if changed:
                horario.save(update_fields=list(defaults.keys()))
    return None


def _assign_jefatura_departamento(request, user):
    plantel_id = (request.POST.get("jefatura_plantel") or "").strip()
    dept_id = (request.POST.get("jefatura_departamento") or "").strip()

    if not plantel_id or not dept_id:
        return None

    plantel = Plantel.objects.filter(id=plantel_id).first()
    if not plantel:
        return "Plantel invalido para jefatura."

    depto = Departamento.objects.select_related("plantel").filter(id=dept_id).first()
    if not depto:
        return "Departamento invalido para jefatura."

    if depto.plantel_id != plantel.id:
        return "El departamento no pertenece al plantel seleccionado."

    _clear_jefatura_if_needed(request, user, keep_id=depto.id)
    depto.jefe = user
    depto.save()
    return None


def _clear_jefatura_if_needed(request, user, keep_id=None):
    qs = Departamento.objects.filter(jefe=user)
    if keep_id:
        qs = qs.exclude(id=keep_id)
    for depto in qs:
        depto.jefe = request.user
        depto.save()
