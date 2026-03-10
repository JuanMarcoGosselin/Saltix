from django.db import models
from django.db.models import Q

class Nomina(models.Model): 
    # Resultado final de nomina por profesor y periodo (totales y fecha).
    profesor = models.ForeignKey("Profesores.Profesor", on_delete=models.PROTECT)
    periodo = models.ForeignKey("Periodo", on_delete=models.PROTECT)
    total_bruto = models.DecimalField(max_digits=12, decimal_places=4)
    total_percepciones = models.DecimalField(max_digits=12, decimal_places=4)
    total_impuestos = models.DecimalField(max_digits=12, decimal_places=4)
    total_deducciones = models.DecimalField(max_digits=12, decimal_places=4) 
    total_neto = models.DecimalField(max_digits=12, decimal_places=4)
    fecha_de_generacion = models.DateTimeField(auto_now_add=True)

class Periodo(models.Model):
    # Periodos de nomina por plantel (solo uno abierto a la vez).
    TIPOS = [
        ("SEMANAL", "Semanal"),
        ("QUINCENAL", "Quincenal"),
        ("MENSUAL", "Mensual"),
    ]
    ESTADOS = [
        ("ABIERTO", "Abierto"),
        ("CERRADO", "Cerrado"),
    ]

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPOS)
    plantel = models.ForeignKey("core.Plantel", on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ABIERTO")
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plantel"],
                condition=Q(estado="ABIERTO"),
                name="un_periodo_abierto_por_plantel",
            )
        ]

class CatalogoConcepto(models.Model):
    # Catalogo de conceptos de percepciones/deducciones y su clasificacion fiscal.
    TIPOS = [
        ("PERCEPCION", "Percepcion"),
        ("DEDUCCION", "Deduccion"),
    ]
    CLASIFICACION_FISCAL = [
        ("GRAVADA", "Gravada"),
        ("EXENTA", "Exenta"),
        ("MIXTA", "Mixta"),
    ]

    nombre = models.CharField(max_length=80)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    clasificacion_fiscal = models.CharField(max_length=10, choices=CLASIFICACION_FISCAL)
    activo = models.BooleanField(default=True)

class DetalleNomina(models.Model): 
    # Partidas que componen la nomina (concepto + monto).
    nomina = models.ForeignKey("Nomina", on_delete=models.CASCADE)
    concepto = models.ForeignKey("CatalogoConcepto", on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=12, decimal_places=4)

class ReciboNomina(models.Model):
    # Recibo PDF generado cuando la nomina se cierra.
    nomina = models.OneToOneField("Nomina", on_delete=models.CASCADE)
    pdf = models.FileField(upload_to="recibos/")
    fecha_emision = models.DateTimeField(auto_now_add=True)

class VistaPreviaNomina(models.Model):
    # Calculo previo de nomina, sin cerrar el periodo.
    periodo = models.ForeignKey("Periodo", on_delete=models.CASCADE)
    generado_por = models.ForeignKey("users.Usuario", on_delete=models.PROTECT)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
