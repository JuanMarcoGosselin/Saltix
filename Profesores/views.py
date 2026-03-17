from django.shortcuts import render
from .models import Profesor 

def dashboard(request):
    usuario = request.user
    profesor = Profesor.objects.get(usuario=usuario.id)
    
    context = {
        "nombrep": profesor.usuario.nombre,
        "salariop": profesor.costo_por_hora,
        "salariomensualp": profesor.costo_por_hora,
        "salarionetop": profesor.costo_por_hora,
        "horasesperadasp": 1,
        "horasp": 2
    }

    return render(request, "Profesores/dashboard.html", context)


