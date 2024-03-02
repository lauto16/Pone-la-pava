from chat.models import Room, RoomIntances, Connected, Message, Banned
from django.contrib.auth.models import User
from html import escape as html_escape
from django.contrib.auth import logout
from glob import escape as py_escape
import logging
import random
import string


logger = logging.getLogger(__name__)


class verifiedSocket():

    """
    This class is meant to be used when a user tries to join a WebSocket and some validations and key generation needs to happen.

        -Room name cleaning
        -Socket code generations
        -Room user capacity validation
        -Users room instances validation

    Atributtes:
        self.error (str, None): Where the last validation error lays 
        self.original_room_name (str): Original room name that user provided
        self.room_name (str, None): Cleaned room name
        self.socket_code (str): Generated socket code
        self.people_amount (int): Validated room capacity
        self.room_instances (bool)= self.verifyRoomInstances(user)

    Methods:
        cleanRoomName(room_name: str, max_length: int): Escapes the name from html and python code,
          does some length and alnum validations, then deletes all blank spaces
          and returns the clean room name 

        codeGenerator(size: int): Using ascii (uppercase/lowercase) letters and digits
          creates a random socket code verifying if it already exists

        setPeopleAmount(people_amount: int/str, default_value: int, max_value: int, min_value: int): First, 
          it converts the people_amount parameter to int, then verifies if it is between the room capacity limits [min_value, max_value] 

        verifyRoomInstances(user: User, max_rooms: int): Verifies whether user 
          can or can not create a room based on room instances number 

        verified(): Searches for validation errors on room name and room instances

        output(): Returns the result of verified function
    """

    def __init__(self, user, room_name, people_amount):

        self.error = None
        self.original_room_name = room_name
        self.room_name = self.cleanRoomName(room_name, max_length=30)
        self.socket_code = self.codeGenerator(size=16)
        self.people_amount = self.setPeopleAmount(
            people_amount=people_amount, default_value=8, max_value=15, min_value=2)
        self.room_instances = self.verifyRoomInstances(user=user, max_rooms=5)

    def cleanRoomName(self, room_name, max_length):
        """
        Cleans the room name escaping from html and python code, verifiyng max length, deleting spaces and not alphanumerics characters

        Returns:
            str: When the cleaning was successfull
            None: When the cleaning was unsuccessfull
        """

        room_name = str(room_name)
        room_name = html_escape(py_escape(room_name))

        if len(room_name) > max_length:
            self.error = 'El nombre de la sala debe tener 30 caracteres como maximo'
            return None

        for char in room_name:
            if not (char.isalnum()):
                self.error = "El nombre no puede contener caracteres no alfanumericos"
                return None

        return room_name.replace(' ', '')

    def codeGenerator(self, size):
        """
        Generates a random code with length = size using string.ascii_uppercase, string.ascii_lowercase and string.digits,
        verifies if the code already exists, in that case, repeats the process

        Returns:
            str: Generated code
        """

        avalaible = False
        new_code = ""
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase

        while not (avalaible):

            new_code = ''.join(random.choice(chars) for _ in range(size))
            found_rooms = list(Room.objects.filter(code=new_code))

            if len(found_rooms) > 0:
                name_number += 1

            else:
                avalaible = True

        return new_code

    def setPeopleAmount(self, people_amount, default_value, max_value, min_value):
        """
        Sets the room capacity to:
            -min_value when user provides a number lower than min_value
            -max_value when user provides a number higher than max_value
            -default_value when user provides a non-integer value
            -people_amount when user provides a number between the max_value and min_value limits (including both)

        Returns:
            int: The normalized people amount value
        """

        if isinstance(people_amount, str):
            for char in people_amount:
                if char.isalpha() or not (char.isalnum()):
                    return default_value

            people_amount = int(people_amount)

        if min_value <= people_amount <= max_value:
            return people_amount

        elif people_amount < 2:
            return min_value

        else:
            return max_value

    def verifyRoomInstances(self, user, max_rooms):
        """
        Verifies whether the user have free room instances or not, based on max_rooms value

        Returns:
            bool: True if user have enough free room instances
            bool: False if user do not have enough free room instances or an DB error ocurred
        """

        try:
            number_room_instances = RoomIntances.objects.get(
                user=user).room_instances

            if number_room_instances < max_rooms:
                return True

            else:
                self.error = "El maximo numero de salas admitido es 5, elimina alguna!"
                return False

        except Exception as e:
            logger.exception('Error: %s', str(e))
            self.error = "Ocurrio un error"
            return False

    def verified(self):
        """
        Check if room name and room instances validations went well

        Returns:
            bool: Representing if the validations where successfull (True) or not (False)
        """

        if self.room_name is None or self.room_instances is False:
            return False

        return True

    def output(self):
        """
        Returns the self.verified instance

        Returns:
            bool: The result of verified instance
        """
        return self.verified()


def banRoomUser(username: str, room: Room):
    """
    Tries to get the user by its username, then creates an Banned register to DB

    Args:
        username (str): User to be banned usernames 
        room (Room): Room instance where the user is going to be banned from

    Returns:
        bool: Transaction was successfull
    """

    try:
        user = User.objects.get(username=username)
        Banned.objects.create(user=user, room=room)
        return True

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def isBanned(user: User, room: Room):
    """
    Searches for a Banned DB register where banned user and room matches user and room arguments

    Args:
        user (User): User probably banned
        room (Room): Room where user might be banned from

    Returns:
        bool: Transaction was successfull
    """

    try:
        Banned.objects.get(user=user, room=room)
        return True
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def createRoomRegister(name: str, code: str, user: User, people_amount: int):
    """
    Creates a Room DB register and adds 1 to user RoomInstances

    Args:
        name (str): Room name
        code (str): Room code
        user (User): Admin user
        people_amount (int): Room capacity

    Returns:
        bool: Transaction was successfull
    """

    try:
        Room.objects.create(name=name, code=code,
                            user=user, people_amount=people_amount)

        user_room_instances = RoomIntances.objects.get(user=user)
        user_room_instances.room_instances += 1
        user_room_instances.save()

        return True

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def updateConnection(user: User, channel_name: str, code_room: str, state: bool):
    """
    Updates the user connection status

    Args:
        user (User): User whose connection will be updated
        channel_name (str): WebSocket channel name (unique for each user)
        code_room (str): The actual room code 
        state (bool): False if disconnected, True if connected

    Returns:
        bool: Transaction was successfull
    """

    try:
        user_is_connected = Connected.objects.get(user=user)
        user_is_connected.channel_name_connected = channel_name
        user_is_connected.code_room_conected = code_room
        user_is_connected.is_connected = state
        user_is_connected.save()

        return True

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def isConnected(user: User):
    """
    Returns a dictionary containing users connection data

    'state': bool
    'connected_room_code': str
    'connected_channel_name': str

    Args:
        user (User): User whose connection data is going to be queried

    Returns:
        dict: A dictionary that contains 
            -Only 'state': bool if user is disconnected
            -'state': bool, 'connected_room_code': str, 'connected_channel_name': str if user is
            connected
    """

    response = {
        'state': False
    }

    try:
        user_is_connected = Connected.objects.get(user=user)

        response = {
            'state': user_is_connected.is_connected,
            'connected_room_code': user_is_connected.code_room_conected,
            'connected_channel_name': user_is_connected.channel_name_connected
        }

    except Exception as e:
        logger.exception('Error: %s', str(e))

    return response


def getUser(request):
    """
    Returns the User instance based on the request argument

    Args:
        request (django request): 

    Returns:
        None: If user does not exist
        User: If user exists
    """

    user = None

    if request.user.is_authenticated:
        user = request.user

    return user


def getUserByName(username: str):
    """
    Returns the User instance based on its username

    Args:
        username (str): The users name to be queried

    Returns:
        None: If user does not exist
        User: If user exists
    """

    try:
        user = User.objects.get(username=username)
        return user
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return None


def getRoomName(room_code: str):
    """
    Returns the Room instance name based on its code

    Args:
        room_code (str): The rooms code to be queried 

    Returns:
        '': If Room does not exist
        str != '': If Room exists
    """

    try:
        return Room.objects.get(code=room_code).name
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return ''


def getRooms(user: User):
    """
    Asks the DB for all the user's rooms.

    Args:
        user (User): The user that owns the rooms

    Returns:
        list: A list that contains all the user's rooms
    """

    rooms = []
    try:
        rooms = list(Room.objects.filter(user=user))
    except Exception as e:
        logger.exception('Error %s', str(e))

    return rooms


def getRoom(room_code):
    """
    Gets a Room instance whose code matches the room_code argument 

    Args:
        room_code (str): Room's code to be queried

    Returns:
        Room: If query found a match
        None: If query didn't find a match
    """

    try:
        return Room.objects.get(code=room_code)
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return None


def deleteRoom(user):
    try:
        connection_data = Connected.objects.get(user=user)
        users_connected = list(Connected.objects.filter(
            code_room_conected=connection_data.code_room_conected))

        room = Room.objects.get(
            user=user, code=connection_data.code_room_conected)

        room.delete()

        return connection_data, users_connected

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False, None


def updateRoomInstances(user):
    try:
        user_rooms = list(Room.objects.filter(user=user))
        room_instances = RoomIntances.objects.get(user=user)

        if room_instances.room_instances >= 0:
            room_instances.room_instances = len(user_rooms)
            room_instances.save()
        else:
            room_instances.room_instances = 0
            room_instances.save()

        return True

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def addMessage(content, user, room_code):
    try:
        room = Room.objects.get(code=room_code)
        Message.objects.create(user=user, content=content, room=room)
        return True
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def getMessages(room_code, user):

    user_messages = {}

    try:
        room = Room.objects.get(code=room_code)
        messages = list(Message.objects.filter(room=room).order_by('date'))

        for i in range(len(messages)):
            message_key = 'message_' + str(i)

            user_messages[message_key] = [

                messages[i].user.username,
                messages[i].content,
                (messages[i].user == user)

            ]

        return user_messages

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def isRoomOwner(rooms, room_code):
    isOwner = False
    for room in rooms:
        if room_code == room.code:
            isOwner = True
            break
    return isOwner


def getRoomUsers(room_code):
    room_connections = []
    try:
        room_connections = list(Connected.objects.filter(
            is_connected=True, code_room_conected=room_code))

    except Exception as e:
        logger.exception('Error: %s', str(e))

    return room_connections


def roomRedirection(data, rooms, user):
    isOwner = False
    room_code = data.get('room_code')
    room_name = data.get('room_name')

    messages = getMessages(room_code=room_code, user=user)

    if messages is False:
        response_data = {
            'success': False,
            'error': 'No se pudo cargar los datos de la sala'
        }

    else:
        isOwner = isRoomOwner(rooms=rooms, room_code=room_code)

        response_data = {
            'success': True,
            'isOwner': isOwner,
            'room_code': room_code,
            'room_name': room_name,
            'room_messages': messages
        }

    return response_data


def getConnected(user, rooms):
    connected_room_data = isConnected(user=user)
    room_code = connected_room_data['connected_room_code']

    room_users = getRoomUsers(room_code=room_code)
    room_usernames = []

    for room_user in room_users:
        room_usernames.append(room_user.user.username)

    response_data = {
        'success': True,
        'room_connected_users': room_usernames,
        'isOwner': isRoomOwner(rooms=rooms, room_code=room_code)
    }

    return response_data


def logoutUser(request):
    logout(request)

    response_data = {
        'success': True
    }

    return response_data


def banUser(user, rooms, data):
    connection_data = isConnected(user=user)

    if connection_data['state'] is False:
        response_data = {
            'success': False,
            'error': 'No estas conectado a la sala'
        }
        return response_data

    room = getRoom(room_code=connection_data['connected_room_code'])

    if room is None:
        response_data = {
            'success': False,
            'error': 'La sala no existe'
        }
        return response_data

    if isRoomOwner(rooms=rooms, room_code=room.code) is False:
        response_data = {
            'success': False,
            'error': 'No eres el administrador de la sala'
        }
        return response_data

    username = data.get('username')

    # you cant ban yourself
    if username == user.username:
        response_data = {
            'success': False,
            'error': 'No puedes expulsarte a ti mismo'
        }
        return response_data

    response_ban_user = banRoomUser(username=username, room=room)

    if response_ban_user is False:
        response_data = {
            'success': False,
            'error': 'No se pudo expulsar al usuario de la sala'
        }
        return response_data

    banned_user = getUserByName(username=username)

    banned_user_connection = isConnected(user=banned_user)

    updateConnection(
        user=banned_user,
        channel_name='',
        code_room='',
        state=False
    )

    response_data = {
        'success': True,
        'banned_username': username,
        'banned_channel_name': banned_user_connection['connected_channel_name']
    }

    return response_data
