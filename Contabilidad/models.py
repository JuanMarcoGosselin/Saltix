from django.db import models

class Nomina(models.Model): 
    profesor = models.ManyToOneRel("Profesor", on_delete=models.PROTECT)
    #???? REVISAR
    periodo = models.ForeignKey("Periodo", on_delete=models.PROTECT)
    total_bruto = models.DecimalField(max_digits=7, decimal_places=2)
    deducciones = models.DecimalField(max_digits=7, decimal_places=2) 
    total_neto = models.DecimalField(max_digits=7, decimal_places=2)
    fecha_de_generacion = models.DateTimeField()
    #profesor_ID_periodo_ID

class Periodo(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=25)

class DetalleNomina(models.Model): 
    nomina_id = models.ForeignKey("Nomina", on_delete=models.CASCADE)
    concepto = models.CharField(max_lenght=25)
    tipo = models.CharField(max_length=25)
    monto = models.DecimalField(max_digits=7, decimal_places=2)