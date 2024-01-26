from .auth_utils import *
from django.contrib.auth import login
from Mate.forms import Login, Register
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def register_view(request):

    error = []
    respuesta = False
    reason = ""

    if request.method == "POST":

        form = Register(request.POST)

        if form.is_valid():

            usuario = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_repeat = form.cleaned_data['password_repeat']

            if password == password_repeat:
                valida, error = validatePassword(password)

                if valida and not error:

                    respuesta, reason = comprobarUser(usuario, email)

                    error = []

                    if respuesta:

                        try:
                            password = passwordHashing(password)
                            User.objects.create(
                                username=usuario, email=email, password=password)

                        except:
                            error.append('No se pudo crear la cuenta')

                        return redirect('login_view')

                else:

                    return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            else:
                error.append("Las contraseñas no son iguales")

        else:
            error.append("El email no es valido")

    else:
        form = Register()

    return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})


def login_view(request):

    error = ""

    if request.method == "POST":

        form = Login(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            resultado, user = verifyPassword(
                username=username, password=password)

            if resultado == 'USER_DOES_NOT_EXISTS' or resultado == False:
                error = "El usuario o la contraseña no son correctos"

            elif resultado == True:

                login(request, user)
                return redirect('lobby')

    else:
        form = Login()

    return render(request, "login.html", {"form": form, "error": error})
