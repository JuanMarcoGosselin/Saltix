from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Asistencias", "0007_asistencia_asistencia_original_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="incidencia",
            name="asistencia_compensatoria",
        ),
        migrations.RemoveField(
            model_name="asistencia",
            name="asistencia_original",
        ),
    ]
