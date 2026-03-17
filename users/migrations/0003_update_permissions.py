from django.db import migrations


def update_permissions(apps, schema_editor):
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
        ("admin.manage_plantel", "Gestionar planteles"),
        ("admin.manage_departamento", "Gestionar departamentos"),
        ("notificaciones.manage_notificacion", "Marcar notificaciones como leidas"),
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

    admin_rol = Rol.objects.filter(nombre__iexact="Administrador").first()
    if not admin_rol:
        admin_rol = Rol.objects.create(
            nombre="Administrador",
            descripcion="Rol administrador",
        )

    admin_permisos = [
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
        "admin.manage_plantel",
        "admin.manage_departamento",
        "notificaciones.manage_notificacion",
    ]

    for codigo in admin_permisos:
        RolPermiso.objects.get_or_create(
            rol=admin_rol,
            permiso=permisos[codigo],
        )


def rollback_permissions(apps, schema_editor):
    Permiso = apps.get_model("users", "Permiso")
    RolPermiso = apps.get_model("users", "RolPermiso")

    codigos = [
        "admin.manage_plantel",
        "admin.manage_departamento",
        "notificaciones.manage_notificacion",
    ]

    permisos = Permiso.objects.filter(codigo__in=codigos)
    RolPermiso.objects.filter(permiso__in=permisos).delete()
    permisos.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_seed_roles_permisos"),
    ]

    operations = [
        migrations.RunPython(update_permissions, rollback_permissions),
    ]
