from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notificacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=120)),
                ("mensaje", models.TextField(max_length=1000)),
                ("tipo", models.CharField(choices=[("info", "Info"), ("success", "Success"), ("warning", "Warning"), ("danger", "Danger")], default="info", max_length=10)),
                ("url", models.CharField(blank=True, max_length=255)),
                ("leida", models.BooleanField(default=False)),
                ("archivada", models.BooleanField(default=False)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-creada_en", "-id"],
                "indexes": [
                    models.Index(fields=["usuario", "leida", "archivada"], name="Notificatio_usuario_425873_idx"),
                    models.Index(fields=["usuario", "creada_en"], name="Notificatio_usuario_1389e0_idx"),
                ],
            },
        ),
    ]
