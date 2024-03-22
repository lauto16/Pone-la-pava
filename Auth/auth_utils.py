import bcrypt
from django.contrib.auth.models import User
from chat.models import RoomInstances, Connected

# SIGN IN Y LOGIN -----------------------------------------------


def validatePassword(password: str):
    """
    Validates a password to see if it meets all the password requirements, if it doesn't, 
    returns a list of the password errors. On the other hand, if it does, returns True 

    Args:
        password (str): An string representing the password

    Returns:
        bool, list: When password did not meet all the requirements
        bool, None: When password did meet all the requirements
    """

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


def verifyPassword(password: str, username: str):
    """
    Verifies if a password is equal to the user's password 

    Args:
        password (str): The password to compare
        username (str): The user's username

    Returns:
        bool, None: If an error ocurred or password is not correct
        bool, User: If the password matches
    """

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


def passwordHashing(password: str):
    """
    Hashes a given password to bcrypt using a salt

    Args:
        password (str): The password to hash

    Returns:
        str: Hashed password
        bool: False if an error ocurred
    """

    try:
        hashed_password_bytes = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password_bytes.decode('utf-8')
        return hashed_password_str
    except:
        return False


def verifyUser(usuario: str, email: str):
    """
    Verifies that username and email doesn't already exists

    Args:
        usuario (str): An username
        email (str): An email

    Returns:
        bool, str: When username or email already exists or username have's a symbol
        bool, None: When neither username or email exists
    """

    for char in usuario:
        if not (char.isalnum()):
            return False, "No se permiten simbolos en el nombre de usuario"

    try:
        user = User.objects.get(username=usuario)
        if user:
            return False, "El nombre de usuario ya existe"

    except (User.DoesNotExist):

        try:
            User.objects.get(email=email)

        except (User.DoesNotExist):
            return True, None

    return False, "Este email ya esta registrado en una cuenta"


def createUserData(user: str, email: str, password: str):
    """
    Creates all user's DB needed registers (User, RoomInstances, Connected)

    Args:
        user (str): User's username
        email (str): User's email
        password (str): User's password

    Returns:
        bool, None: When transaction was successfull
        bool, str: When an error ocurred
    """

    try:
        new_user = User.objects.create(
            username=user, email=email, password=password)

        RoomInstances.objects.create(
            user=new_user, room_instances=0)

        Connected.objects.create(
            user=new_user, is_connected=False, code_room_conected="", channel_name_connected="")

        return True, None

    except:
        return False, "Error al crear el usuario"
