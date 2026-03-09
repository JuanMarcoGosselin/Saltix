from django.db import models

class Asistencia(models.Model): 
    id_profesor = models.ForeignKey("Profesor", on_delete=models.PROTECT)
    fecha = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    estado = models.CharField(max_lenght=25)
    justificada = models.BooleanField
    observaciones = models.TextField(max_length= 1000)
    profesor_id_fecha = models.ForeignKey("Horario", on_delete=models.CASCADE)

class Incidencia(models.Model): 
    asistencia_id = models.ForeignKey("Asistencia", on_delete=models.CASCADE)
    motivo = models.TextField(max_length=1000)
    estado = models.CharField(max_lenght = 25)
    aprobado_por = models.ForeignKey("Usuario", on_delete=models.PROTECT)
    fecha_de_resolucion =  models.DateTimeField()