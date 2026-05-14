# Generated manually for Sprint 4 jefatura dashboard updates.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_initial"),
        ("jefatura", "0002_initial"),
        ("Profesores", "0007_remove_profesor_departamentos_and_more"),
        ("users", "0003_update_permissions"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitudTransferencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motivo", models.TextField(max_length=1000)),
                ("estado", models.CharField(choices=[("PENDIENTE", "Pendiente"), ("APROBADA", "Aprobada"), ("RECHAZADA", "Rechazada"), ("CANCELADA", "Cancelada")], default="PENDIENTE", max_length=10)),
                ("observaciones", models.TextField(blank=True, max_length=1000)),
                ("fecha_solicitud", models.DateTimeField(auto_now_add=True)),
                ("fecha_resolucion", models.DateTimeField(blank=True, null=True)),
                ("departamento_destino", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_recibidas", to="users.departamento")),
                ("departamento_origen", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_solicitadas", to="users.departamento")),
                ("plantel_destino", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_entrada", to="core.plantel")),
                ("plantel_origen", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_salida", to="core.plantel")),
                ("profesor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="solicitudes_transferencia", to="Profesores.profesor")),
                ("responsable", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_resueltas", to=settings.AUTH_USER_MODEL)),
                ("solicitante", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transferencias_creadas", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name="solicitudtransferencia",
            index=models.Index(fields=["estado", "fecha_solicitud"], name="jefatura_so_estado_283e9c_idx"),
        ),
        migrations.AddIndex(
            model_name="solicitudtransferencia",
            index=models.Index(fields=["profesor", "fecha_solicitud"], name="jefatura_so_profeso_4f327a_idx"),
        ),
        migrations.AddIndex(
            model_name="solicitudtransferencia",
            index=models.Index(fields=["departamento_origen", "estado"], name="jefatura_so_depart_20f539_idx"),
        ),
        migrations.AddIndex(
            model_name="solicitudtransferencia",
            index=models.Index(fields=["departamento_destino", "estado"], name="jefatura_so_depart_d49c74_idx"),
        ),
    ]
