from .auth_utils import *
from Mate.utils import getUser
from django.contrib.auth import login
from Mate.forms import Login, Register
from django.shortcuts import render, redirect


def register_view(request):
    """
    Sign up view

    Args:
        request (django request): The user's request

    Returns:
        HttpResponse: Sign up error data
        HttpResponseRedirect: When sign up data was valid
    """

    error = []
    respuesta = False
    reason = ""

    if request.method == "POST":

        form = Register(request.POST)

        if form.is_valid():

            user = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_repeat = form.cleaned_data['password_repeat']

            if password != password_repeat:
                error.append("Las contraseñas no son iguales")
                return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            valida, error = validatePassword(password)

            if valida is False:
                return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            respuesta, reason = verifyUser(user, email)

            if respuesta is False:
                return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            password = passwordHashing(password)

            if password is False:
                error = []
                error.append("No se pudo crear la cuenta")
                return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            response_create_user_data, reason = createUserData(
                user=user, email=email, password=password)

            if response_create_user_data is False:
                return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})

            return redirect('login_view')

    else:
        form = Register()

    return render(request, "register.html", {"form": form, "error": error, 'error_bd': respuesta, "datos_error": reason})


def login_view(request):
    """
    Sign in view

    Args:
        request (django request): The user's request

    Returns:
        HttpResponse: Sign in error data
        HttpResponseRedirect: When sign in data was valid or user is already logged in
    """

    user = getUser(request)

    if user is not None:
        return redirect('lobby')

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
                return render(request, "login.html", {"form": form, "error": error})

            login(request, user)
            return redirect('lobby')

    else:
        form = Login()

    return render(request, "login.html", {"form": form, "error": error})
