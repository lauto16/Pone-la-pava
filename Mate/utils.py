from chat.models import Room, RoomIntances, Connected, Message, Banned
from django.contrib.auth.models import User
from html import escape as html_escape
from glob import escape as py_escape
import logging


logger = logging.getLogger(__name__)


class verifiedSocket():

    def __init__(self, user, room_name, people_amount):

        self.original_room_name = room_name
        self.room_name = self.cleanRoomName(room_name)
        self.socket_code = self.codeGenerator(name=self.room_name)
        self.people_amount = self.setPeopleAmount(people_amount=people_amount)
        self.room_instances = self.verifyRoomInstances(user)

    def cleanRoomName(self, room_name):
        room_name = str(room_name)
        room_name = html_escape(py_escape(room_name))

        if len(room_name) > 30:
            return None

        for char in room_name:
            if char.isalnum():
                return room_name.replace(' ', '')

        return None

    def codeGenerator(self, name):

        avalaible = False
        name_number = 0

        while not (avalaible):
            new_code = name + str(name_number)
            found_rooms = list(Room.objects.filter(code=new_code))

            if len(found_rooms) > 0:
                name_number += 1

            else:
                avalaible = True

        return new_code

    def setPeopleAmount(self, people_amount):

        default_value = 8
        max_value = 15
        min_value = 2

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

    def verifyRoomInstances(self, user):
        try:
            number_room_instances = RoomIntances.objects.get(
                user=user).room_instances

            if number_room_instances < 5:
                return True

            else:
                return None

        except Exception as e:
            logger.exception('Error: %s', str(e))
            return None

    def verified(self):

        if self.room_name is None or self.room_instances is None:
            return False

        return True

    def output(self):
        return self.verified()


def createAdmision(user, room):
    try:
        AdmitedUser.objects.create(user=user, room=room)
        return True
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def isBanned(user, room):
    try:
        # user is banned
        Banned.objects.get(user=user, room=room)
        return True
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return False


def createRoomRegister(name, code, user, people_amount):
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


def updateConnection(user, channel_name, code_room, state):
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


def isConnected(user):

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
    user = None

    if request.user.is_authenticated:
        user = request.user

    return user


def getRoomName(room_code):
    try:
        return Room.objects.get(code=room_code).name
    except Exception as e:
        logger.exception('Error: %s', str(e))
        return ''


def getRooms(user):

    rooms = []
    try:
        rooms = list(Room.objects.filter(user=user))
    except Exception as e:
        logger.exception('Error %s', str(e))

    return rooms


def getRoom(room_code):
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
