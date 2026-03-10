from django.db import migrations


def seed_roles_permisos(apps, schema_editor):
    Rol = apps.get_model("users", "Rol")
    Permiso = apps.get_model("users", "Permiso")
    RolPermiso = apps.get_model("users", "RolPermiso")

    permisos_def = [
        ("users.manage_users", "Gestionar usuarios"),
        ("users.manage_roles", "Gestionar roles y permisos"),
        ("profesores.manage_profesores", "Gestionar profesores"),
        ("profesores.manage_horarios", "Gestionar horarios"),
        ("asistencias.capturar_asistencia", "Capturar asistencia"),
        ("asistencias.captura_manual", "Captura manual de asistencia"),
        ("asistencias.solicitar_correccion", "Solicitar correccion de asistencia"),
        ("asistencias.aprobar_incidencias", "Aprobar incidencias"),
        ("contabilidad.configurar_periodos", "Configurar periodos de nomina"),
        ("contabilidad.calcular_nomina", "Calcular nomina"),
        ("contabilidad.cerrar_nomina", "Cerrar nomina"),
        ("contabilidad.ver_recibos", "Ver/descargar recibos"),
        ("reportes.ver_reportes", "Ver reportes administrativos"),
        ("notificaciones.enviar", "Enviar notificaciones"),
        ("auditoria.ver_bitacora", "Ver bitacora de auditoria"),
    ]

    permisos = {}
    for codigo, descripcion in permisos_def:
        permiso, _ = Permiso.objects.get_or_create(
            codigo=codigo,
            defaults={"descripcion": descripcion},
        )
        if permiso.descripcion != descripcion:
            permiso.descripcion = descripcion
            permiso.save(update_fields=["descripcion"])
        permisos[codigo] = permiso

    roles_def = {
        "Administrador": [
            "users.manage_users",
            "users.manage_roles",
            "profesores.manage_profesores",
            "profesores.manage_horarios",
            "asistencias.capturar_asistencia",
            "asistencias.captura_manual",
            "asistencias.solicitar_correccion",
            "asistencias.aprobar_incidencias",
            "contabilidad.configurar_periodos",
            "contabilidad.calcular_nomina",
            "contabilidad.cerrar_nomina",
            "contabilidad.ver_recibos",
            "reportes.ver_reportes",
            "notificaciones.enviar",
            "auditoria.ver_bitacora",
        ],
        "Jefatura": [
            "profesores.manage_profesores",
            "profesores.manage_horarios",
            "asistencias.capturar_asistencia",
            "asistencias.captura_manual",
            "asistencias.aprobar_incidencias",
            "reportes.ver_reportes",
            "notificaciones.enviar",
        ],
        "Contabilidad": [
            "contabilidad.configurar_periodos",
            "contabilidad.calcular_nomina",
            "contabilidad.cerrar_nomina",
            "contabilidad.ver_recibos",
            "reportes.ver_reportes",
        ],
        "Profesor": [
            "asistencias.capturar_asistencia",
            "asistencias.solicitar_correccion",
            "contabilidad.ver_recibos",
        ],
    }

    for nombre, permisos_codigos in roles_def.items():
        rol, _ = Rol.objects.get_or_create(
            nombre=nombre,
            defaults={"descripcion": f"Rol {nombre.lower()}"},
        )
        RolPermiso.objects.filter(rol=rol).delete()
        for codigo in permisos_codigos:
            RolPermiso.objects.get_or_create(rol=rol, permiso=permisos[codigo])


def unseed_roles_permisos(apps, schema_editor):
    Rol = apps.get_model("users", "Rol")
    Permiso = apps.get_model("users", "Permiso")
    RolPermiso = apps.get_model("users", "RolPermiso")

    roles = Rol.objects.filter(nombre__in=["Administrador", "Jefatura", "Contabilidad", "Profesor"])
    RolPermiso.objects.filter(rol__in=roles).delete()
    roles.delete()
    Permiso.objects.filter(codigo__startswith="users.").delete()
    Permiso.objects.filter(codigo__startswith="profesores.").delete()
    Permiso.objects.filter(codigo__startswith="asistencias.").delete()
    Permiso.objects.filter(codigo__startswith="contabilidad.").delete()
    Permiso.objects.filter(codigo__startswith="reportes.").delete()
    Permiso.objects.filter(codigo__startswith="notificaciones.").delete()
    Permiso.objects.filter(codigo__startswith="auditoria.").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles_permisos, unseed_roles_permisos),
    ]
