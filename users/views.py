from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_redirect_for_role(request.user))

    error = ""
    if request.method == "POST":
        email = request.POST.get("email") or request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(_redirect_for_role(user))
        error = "Credenciales invalidas."

    return render(request, "users/login.html", {"error": error})


def _redirect_for_role(user):
    role = ""
    if getattr(user, "rol_id", None) and user.rol_id.nombre:
        role = user.rol_id.nombre.lower()

    if role == "jefatura":
        return "jefatura_dashboard"
    if role == "profesor":
        return "profesores_dashboard"
    if role in {"administrador", "admin"}:
        return "admin_dashboard"

    return "admin:index"
