# Generated manually for Sprint 4 cleanup.

from django.db import migrations


def copiar_transferencias(apps, schema_editor):
    TransferenciaDepartamento = apps.get_model("Profesores", "TransferenciaDepartamento")
    SolicitudTransferencia = apps.get_model("jefatura", "SolicitudTransferencia")

    for anterior in TransferenciaDepartamento.objects.select_related(
        "profesor",
        "profesor__plantel",
        "departamento_origen",
        "departamento_origen__plantel",
        "departamento_origen__jefe",
        "departamento_destino",
        "departamento_destino__plantel",
    ):
        solicitante_id = anterior.aprobado_por_id or anterior.departamento_origen.jefe_id
        if not solicitante_id:
            continue

        SolicitudTransferencia.objects.create(
            profesor_id=anterior.profesor_id,
            departamento_origen_id=anterior.departamento_origen_id,
            departamento_destino_id=anterior.departamento_destino_id,
            plantel_origen_id=anterior.departamento_origen.plantel_id or anterior.profesor.plantel_id,
            plantel_destino_id=anterior.departamento_destino.plantel_id,
            motivo="Historial migrado desde Profesores.TransferenciaDepartamento.",
            estado="APROBADA",
            solicitante_id=solicitante_id,
            responsable_id=anterior.aprobado_por_id,
            observaciones="Transferencia historica migrada al modulo de Jefatura.",
            fecha_solicitud=anterior.fecha,
            fecha_resolucion=anterior.fecha,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("Profesores", "0007_remove_profesor_departamentos_and_more"),
        ("jefatura", "0003_solicitudtransferencia"),
    ]

    operations = [
        migrations.RunPython(copiar_transferencias, migrations.RunPython.noop),
        migrations.DeleteModel(
            name="TransferenciaDepartamento",
        ),
    ]
