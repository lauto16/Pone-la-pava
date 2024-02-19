import bcrypt
from django.contrib.auth.models import User
from chat.models import RoomIntances, Connected

# SIGN IN Y LOGIN -----------------------------------------------


def validatePassword(password):

    password = password.lower()
    symbols = False
    numbers = False
    tilde_espacio = False

    for i in password:

        if i in ("áéíóú") or i == " ":
            tilde_espacio = True
        if not i.isalnum():
            symbols = True
        if i.isdigit():
            numbers = True

    error_messages = []

    if len(password) < 10:
        error_messages.append(
            "La contraseña debe contener al menos 10 caracteres")

    if not symbols:
        error_messages.append(
            "La contraseña debe contener al menos un símbolo")

    if not numbers:
        error_messages.append("La contraseña debe contener al menos un número")

    if tilde_espacio:
        error_messages.append(
            "La contraseña no debe contener tildes o espacios")

    if not error_messages:
        return True, None

    return False, error_messages


def verifyPassword(password, username):
    try:
        usuario = User.objects.get(username=username)

    except:
        return 'USER_DOES_NOT_EXISTS', None

    try:
        hashed_password = usuario.password.encode('utf-8')
        if (bcrypt.checkpw(password.encode('utf-8'), hashed_password)):
            return True, usuario
    except:
        return False, None

    return False, None


def passwordHashing(password):
    try:
        hashed_password_bytes = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password_bytes.decode('utf-8')
        return hashed_password_str
    except:
        return False


def comprobarUser(usuario, email):

    for char in usuario:
        if not (char.isalnum()):
            return False, "No se permiten simbolos en el nombre de usuario"

    try:
        user = User.objects.get(username=usuario)
        if user:
            return False, "El nombre de usuario ya existe"

    except:

        try:
            User.objects.get(email=email)

        except:
            return True, None

    return False, "Este email ya esta registrado en una cuenta"


def createUserData(user, email, password):
    try:
        new_user = User.objects.create(
            username=user, email=email, password=password)

        RoomIntances.objects.create(
            user=new_user, room_instances=0)

        Connected.objects.create(
            user=new_user, is_connected=False, code_room_conected="", channel_name_connected="")

        return True, None

    except:
        return False, "Error al crear el usuario"
