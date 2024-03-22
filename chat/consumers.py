import json
from Mate.utils import (verifiedSocket,
                        createRoomRegister,
                        updateConnection,
                        isConnected,
                        getRoomName,
                        getRoom,
                        deleteRoom,
                        updateRoomInstances,
                        addMessage,
                        isBanned)
from channels.exceptions import DenyConnection, StopConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from html import escape as html_escape
from glob import escape as py_escape
import logging


class ChatConsumer(WebsocketConsumer):
    """
    A WebsocketConsumer used for the chat rooms
    """

    def connect(self):
        """
        Handles two types of requests sent by user using url scope:
            -Create: Create a room
            -Join: Join a room

        Raises:
            DenyConnection: When an error ocurred 
        """

        self.action = self.scope['url_route']['kwargs']['action']
        self.user = self.get_user(self.scope)
        self.room_code = 0
        logger = logging.getLogger(__name__)

        # try to disconnect the user before connecting or creating a new room
        try:
            connection = isConnected(self.user)
            if connection['state'] is True:
                self.disconnect(close_code=1000)
        except Exception as e:
            logger.exception('Error: %s', str(e))

        # create a room
        if self.action == 'create':

            received_room_name = self.scope['url_route']['kwargs']['room_name_code']
            received_people_amount = self.scope['url_route']['kwargs']['people_amount']

            validator = verifiedSocket(
                user=self.user, people_amount=received_people_amount, room_name=received_room_name)

            # validation failed
            if validator.output() is False:
                self.error_handler(error=validator.error, action='connect')
                raise DenyConnection

            self.room_code = validator.socket_code
            self.room_name = validator.original_room_name
            self.people_amount = validator.people_amount

            async_to_sync(self.channel_layer.group_add)(
                self.room_code,
                self.channel_name
            )

            response_oncreate = createRoomRegister(
                name=self.room_name,
                code=self.room_code,
                user=self.user,
                people_amount=self.people_amount
            )

            # creation failed
            if response_oncreate is False:
                self.error_handler(
                    error='No se pudo crear la sala', action='connect')
                raise DenyConnection

            self.accept()

            # return the code to the room creator
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'room_code_message',
                }

            )

        # join a room by code
        elif self.action == 'join':

            response_is_connected = isConnected(user=self.user)

            self.room_code = self.scope['url_route']['kwargs']['room_name_code']

            room = getRoom(room_code=self.room_code)

            # room doesn't exists
            if room is None:
                self.error_handler(error='La sala no existe', action='connect')
                raise DenyConnection

            # verify if codes are the same (because of the not case sensitive django ORM behavior)
            if room.code != self.room_code:
                self.error_handler(error='La sala no existe', action='connect')
                raise DenyConnection

            response_is_banned = isBanned(user=self.user, room=room)

            # user is banned of the room
            if response_is_banned is True:
                self.error_handler(
                    error='No puedes ingresar a esta sala, has sido expulsado', action='connect')
                raise DenyConnection

            max_connections = room.people_amount

            async_to_sync(self.channel_layer.group_add)(
                self.room_code,
                self.channel_name
            )

            # room capacity exceded
            if len(self.channel_layer.groups[self.room_code]) > max_connections:
                self.error_handler(
                    error='No puedes ingresar a esta sala, esta llena', action='connect')
                raise DenyConnection

            self.accept()

            print(
                self.room_code + ': ',
                len(self.channel_layer.groups[self.room_code]),
                "/", max_connections
            )

            updateConnection(
                user=self.user,
                channel_name=self.channel_name,
                code_room=self.room_code,
                state=True
            )

    def error_handler(self, error: str, action: str):
        """
        Handles two types of actions:
            -Connect error
            -Other error

        When action is 'connect', sends the error to frontend and disconnects the user
        When action is 'other', it only sends the error to frontend 

        Args:
            error (str): Error description
            action (str): Error handler error type ('connect' or 'other')
        """
        if action == 'connect':
            self.accept()
            self.send(text_data=json.dumps({
                'type': 'error',
                'error': error
            }))
            self.create_disconnect(close_code=1000)

        elif action == 'other':
            self.send(text_data=json.dumps({
                'type': 'error',
                'error': error
            }))

    def disconnect(self, close_code):
        """
        Basic disconnect from webSocket

        Args:
            close_code (int): ChatConsumer's close code

        Raises:
            StopConsumer: So the consumer closes

        Returns:
            None: If the user is already disconnected
        """

        print('disconnecting user from ', self.room_code)

        disconnect_data = isConnected(user=self.user)

        if disconnect_data['state'] is False:
            return

        if disconnect_data['connected_room_code'] in self.channel_layer.groups:
            async_to_sync(self.channel_layer.group_discard)(
                disconnect_data['connected_room_code'],
                disconnect_data['connected_channel_name']
            )

        updateConnection(
            user=self.user, channel_name="", code_room="", state=False)

        raise StopConsumer

    def create_disconnect(self, close_code):
        """
        This function gets called when a room is created, so the user doesn't 
        automatically connect to it

        Args:
            close_code (int): ChatConsumer's close code

        """

        async_to_sync(self.channel_layer.group_discard)(
            self.room_code,
            self.channel_name
        )

        self.close()

    def ban_disconnect(self, channel_name: str, close_code):
        """
        This function gets called when an user is banned from a room, disconnecting him from it

        Args:
            channel_name (str): The room's channel name
            close_code (_type_): ChatConsumer's close code

        """
        if self.room_code in self.channel_layer.groups:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_code,
                channel_name
            )

    def delete_disconnect(self, data, close_code):
        """
        This function gets called when a room is removed

        Args:
            data (Connected): A Connected DB register containing user's connection data
            close_code (int): ChatConsumer's close code

        """
        print('disconnecting ', data.user, ' from ', data.code_room_conected)
        if data.code_room_conected in self.channel_layer.groups:
            async_to_sync(self.channel_layer.group_discard)(
                data.code_room_conected,
                data.channel_name_connected
            )

        updateConnection(
            user=data.user, channel_name="", code_room="", state=False)

    def receive(self, text_data):
        """
        Handles all the messages that user can receive, message_type can be:
            -delete_socket: disconnects user from room
            -redirect_room: redirect the user to the room
            -delete: remove a room
            -ban_user: ban a user from room
            -others(always treat it like a chat message): chat message

        """

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json['type']
        connection = isConnected(user=self.user)

        # disconnection from chat room
        if message_type == 'delete_socket':

            # if there's no users in the room, close it
            if len(self.channel_layer.groups[self.room_code]) == 1:
                self.close()

            self.disconnect(close_code=1000)

        # send redirect message to the front-end
        elif message_type == 'redirect_room':
            self.send(text_data=json.dumps({
                'type': 'room_redirection',
                'room_name': getRoomName(self.room_code),
                'room_code': self.room_code
            }))

        # delete a room
        elif message_type == 'delete':

            connection_data = isConnected(user=self.user)

            if connection_data['state'] is False:
                self.error_handler(
                    error='No estas conectado a ninguna sala', action='other')
                return

            room_user_id = getRoom(
                room_code=connection_data['connected_room_code']).user.id

            if self.user.id != room_user_id:
                self.error_handler(
                    error='Intentaste eliminar una sala que no es tuya', action='other')
                return

            connection_data, users_connected = deleteRoom(user=self.user)

            for user_con in users_connected:
                self.delete_disconnect(
                    close_code=1000, data=user_con)

            updateRoomInstances(user=self.user)
            self.close()

        # ban a user from a room
        elif message_type == 'ban_user':
            self.ban_disconnect(
                close_code=1000, channel_name=text_data_json['channel_name'])
            return

        # chat message
        else:

            if isConnected(self.user)['state'] is False:
                self.error_handler(
                    error='No estas conectado a ninguna sala', action='other')
                return

            room = getRoom(room_code=connection['connected_room_code'])

            if room is None:
                self.error_handler(
                    error='La sala a la que estas conectado ya no existe', action='other')

            if isBanned(user=self.user, room=room) is True:
                self.error_handler(
                    error='Fuiste expulsado de la sala, no puedes enviar mensajes', action='other')

            if len(message) < 1:
                return

            # escaping characters
            message = html_escape(py_escape(message))

            async_to_sync(self.channel_layer.group_send)(
                connection['connected_room_code'],
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.user.username
                }
            )

            addMessage(content=message, user=self.user,
                       room_code=self.room_code)

    def chat_message(self, event):
        """
        Sends a chat message to the WebSocket

        Returns:
            None: If the user is disconnected

        """

        message = event['message']
        username = event['username']
        isUser = self.user.username == username

        if isConnected(self.user)['state'] is False:
            return

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username,
            'isUser': isUser
        }))

    def room_code_message(self, event):
        """
        Sends a message containing the room code and name to frontend

        """
        self.send(text_data=json.dumps({
            'type': 'room_created',
            'room_code': self.room_code,
            'room_name': self.room_name
        }))

        # close connection after creating room
        self.create_disconnect(close_code=1000)

    def get_user(self, scope):
        """
        Gets the user using scope

        Args:
            scope (url_scope): The request url scope 

        Returns:
            User: User
        """
        user = None
        if scope['user'].is_authenticated:
            user = scope['user']
        return user


if __name__ == '__main__':
    pass
