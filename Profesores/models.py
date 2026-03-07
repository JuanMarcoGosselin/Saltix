from django.db import models

class Profesor(models.Model): 
    usuario_id = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    rfc = models.CharField(max_length=13)
    curp = models.CharField(max_length=18)
    telefono = models.CharField(max_length=10)
    direcion = models.TextField(max_length=100)
    fecha_ingreso = models.DateField()
    estado_laboral = models.CharField(max_length=25)
    #7 por si hay inflacion bro 
    salario_por_hora = models.DecimalField(max_digits=7, decimal_places=2)
    tipo_contrato = models.CharField(max_length=25)
    departamento = models.ForeignKey("Departamento", on_delete=models.PROTECT, null=True)

class Horario(models.Model): 
    DIAS = [
        ("LUN", "Lunes"),
        ("MAR", "Martes"),
        ("MIE", "Miercoles"), 
        ("JUE", "Jueves")
        ("VIE", "Viernes")
        ("SAB", "Sabado")
    ]
    profesor_id = models.ForeignKey("Profesor", on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=10)