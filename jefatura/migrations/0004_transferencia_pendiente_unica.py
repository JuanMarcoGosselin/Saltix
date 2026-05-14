from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jefatura", "0003_solicitudtransferencia"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="solicitudtransferencia",
            constraint=models.UniqueConstraint(
                fields=("profesor",),
                condition=models.Q(estado="PENDIENTE"),
                name="unique_transferencia_pendiente_profesor",
            ),
        ),
    ]
