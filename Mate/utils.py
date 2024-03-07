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


def getRoom(room_code: str):
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


def deleteRoom(user: User):
    """
    Gets the users connected to a room, then removes the Room's DB register

    Args:
        user (User): User that will be used to query and find the room that he is in

    Returns:
        Connected, list[Connected]: The user's connection data and a list containing data for users connected to that room 
        False, None: Representing an error ocurred or there was no data to return
    """
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


def updateRoomInstances(user: User):
    """
    Updates the user's RoomInstances DB register matching it to the total of rooms that user owns, only if 
    the number of instances is between 5 and 0, including both of them.


    Args:
        user (User): User whose RoomInstances will be update

    Returns:
        bool: Transaction was successfull
    """

    try:
        user_rooms = list(Room.objects.filter(user=user))
        room_instances = RoomIntances.objects.get(user=user)

        if 5 >= room_instances.room_instances >= 0:
            room_instances.room_instances = len(user_rooms)
            room_instances.save()
        else:
            room_instances.room_instances = 5
            room_instances.save()

        return True

    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def addMessage(content: str, user: User, room_code: str):
    """
    Creates a new Message DB register 

    Args:
        content (str): The content of the message
        user (User): The sender user 
        room_code (str): The room's code where the message is going to be sent

    Returns:
        bool: Transaction was successfull
    """
    try:
        room = Room.objects.get(code=room_code)
        Message.objects.create(user=user, content=content, room=room)
        return True
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def getMessages(room_code: str, user: User):
    """
    Revovers all the messages from a room, returning sender username, message content and isOwner(bool)

    Args:
        room_code (str): The code of the room whose messages will be queried
        user (User): The user that made the request

    Returns:
        dict{list}: A dictionary where each key represents
        a different message, and each message is a list that contains [username, content, isOwner]
        bool: False if an error ocurred
    """

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


def isRoomOwner(rooms: list, room_code: str):
    """
    Compares a given room code to each room.room_code in the rooms array looking for a match

    Args:
        rooms (list[Room]): A list of Room instances
        room_code (str): The code of the room that is going to be compared to all the user's rooms codes

    Returns:
        bool: User is the owner of the room
    """

    for room in rooms:
        if room_code == room.code:
            return True
    return False


def roomRedirection(data, rooms: list, user: User):
    """
    Returns all the necessary data to redirect the user to a certain room

    Args:
        data (django request): The users request
        rooms (list[Room]): A list containing all the rooms
        user (User): The user to get redirected

    Returns:
        dict: When a error ocurred {
            'success': False (bool), 
            'error': Error data (str)
            }

        dict: When transaction was successfull {
            'success': True (bool),
            'isOwner' User is the owner of the room (bool),
            'room_code': The room's code (str),
            'room_name': The room's code (str),
            'room_messages': A dict returned by getMessages containing all the rooms messages (dict)
            }
    """

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


def getConnected(user: User, rooms: list, get_connected: bool):
    """
    Asks the database for all the users connected to a room

    Args:
        user (User): The user that requested the connected users
        rooms (list): A list that contains all the users Rooms

    Returns:
        dict: {
        'success': (bool),
        'room_connected_users': All the connected users (list[User]),
        'room_connected_users': All the connected user's names (list[str]),
        'isOwner': Is the user the room's owner? (bool)
        }
    """
    connected_room_data = isConnected(user=user)
    room_code = connected_room_data['connected_room_code']

    room_connections = []
    room_usernames = []

    try:
        room_connections = list(Connected.objects.filter(
            is_connected=True, code_room_conected=room_code))

        for connection in room_connections:
            room_usernames.append(connection.user.username)

    except Exception as e:
        logger.exception('Error: %s', str(e))
        # reset the variables so the user dont get a sliced list or a None
        room_connections = []
        room_usernames = []

    if get_connected is True:

        response_data = {
            'success': True,
            'room_connected_usernames': room_usernames,
            'room_connected_users': room_connections,
            'isOwner': isRoomOwner(rooms=rooms, room_code=room_code)
        }

        return response_data

    response_data = {
        'success': True,
        'room_connected_usernames': room_usernames,
        'isOwner': isRoomOwner(rooms=rooms, room_code=room_code)
    }

    return response_data


def logoutUser(request):
    """
    Logs the user out

    Args:
        request (django request): The user's request

    Returns:
        dict: {
            success: (bool)
            }
    """

    logout(request)

    response_data = {
        'success': True
    }

    return response_data


def validateAdmin(user: User, rooms: list):
    """
    The necessary validations to see if a user is admin

    Args:
        user (User): The user that is going to be validated
        rooms (list): A list containing all user's rooms

    Returns:
        dict: If transaction was successfull {
        'success': True (bool),
        'room': The room where the user is connected (Room)
        }

        dict: If transaction was not successfull {
        'success': False (bool),
        'error': The error message (str)
    }


    """

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

    return {
        'success': True,
        'room': room
    }


def banUser(user: User, rooms: list, data):
    """
    Firt, it do some admin validations, then, creates a Banned DB register and finally, clears
    the Connected user's register


    Args:
        user (User): The room's admin
        rooms (list[Room]): A list containing all the admin's rooms
        data (django request): A request containing the data from the user that is going to be banned

    Returns:
        dict: If transaction was successfull {
        'success': True (bool),
        'banned_username': The banned user's username (str),
        'banned_channel_name': The banned user's channel name (str)
        }

        dict: If transaction was not successfull {
        'success': False (bool),
        'error' The error message (str)
        }
    """

    validation = validateAdmin(user=user, rooms=rooms)

    if validation['success'] is False:
        return validation

    username = data.get('username')

    # you can't ban yourself
    if username == user.username:
        response_data = {
            'success': False,
            'error': 'No puedes expulsarte a ti mismo'
        }
        return response_data

    response_ban_user = banRoomUser(username=username, room=validation['room'])

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


if __name__ == '__main__':
    pass
