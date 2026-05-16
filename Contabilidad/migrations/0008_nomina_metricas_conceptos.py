from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Contabilidad", "0007_remove_periodo_un_periodo_abierto_por_plantel_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="nomina",
            name="faltas",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="nomina",
            name="faltas_equivalentes",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="nomina",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="nomina",
            name="horas_trabajadas",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="nomina",
            name="retardos",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="detallenomina",
            name="creado_en",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name="detallenomina",
            name="descripcion",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="nomina",
            name="estado",
            field=models.CharField(choices=[("pendiente", "Pendiente"), ("procesando", "Procesando"), ("cerrada", "Cerrada"), ("pagada", "Pagada")], default="procesando", max_length=20),
        ),
        migrations.AddIndex(
            model_name="nomina",
            index=models.Index(fields=["periodo", "estado"], name="Contabilida_periodo_19132d_idx"),
        ),
        migrations.AddIndex(
            model_name="nomina",
            index=models.Index(fields=["profesor", "periodo"], name="Contabilida_profeso_b70e23_idx"),
        ),
        migrations.AddConstraint(
            model_name="nomina",
            constraint=models.UniqueConstraint(fields=("profesor", "periodo"), name="unique_nomina_profesor_periodo"),
        ),
        migrations.AddConstraint(
            model_name="periodo",
            constraint=models.UniqueConstraint(fields=("fecha_inicio", "fecha_fin", "tipo"), name="unique_periodo_rango_tipo"),
        ),
    ]
