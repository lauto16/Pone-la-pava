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

    # documentation
    """

    VARIABLES IMPORTANTES:
    self.room_code --> codigo para ingresar a una sala
    self.room_name --> nombre de la sala
    self.channel_name --> nombre asignado a la instancia webSocket del usuario


    connect: recibe 3 tipos de peticiones: 
        -create -> valida que todo el usuario cumpla los requerimientos
                   y que los argumentos de creacion sean correctos mediante 
                   verifiedSocket, crea una nueva sala, la agrega a la BD.

        -join -> valida que el usuario no se encuentre ya en una sala, luego
        verifica que la sala exista en la base de datos, agrega al usuario a la
        sala y modifica el registro de Connected (donde se almacena la sala en la
        que se encuentra el usuario).


        -delete -> elimina la sala de la bd, asi como los registros de conexion, 
        desconecta a todos los usuarios que pudieran estar conectados y modifica el valor
        de RoomInstances del usuario.

    disconnect: obtiene los datos de la sala actual mediante isConnected y cierra la conexion,
                luego resetea Connection y hace raise StopConsumer para detener la clase. En caso de
                que no quede nadie en la sala, se cierra la sala.


    receive: recibe los datos del frontend, tiene 2 peticiones:
            - 'delete_socket' -> desconecta al usuario del socket
            - 'chat_message' -> recepcion y reenvio de mensajes al front  si el usuario esta 
                                conectado y el mensaje no esta vacio.

    get_user: obtiene el usuario que envio la peticion.


    delete_disconnect: desconecta a todos los usuarios dentro de la sala.
    """

    def connect(self):

        self.action = self.scope['url_route']['kwargs']['action']
        self.user = self.get_user(self.scope)
        print("USUARIO: ", self.user)
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

            if response_is_connected['state'] is True:
                return
            self.room_code = self.scope['url_route']['kwargs']['room_name_code']

            room = getRoom(room_code=self.room_code)

            # room doesn't exists
            if room is None:
                return

            # verify if codes are the same (because of the not case sensitive django ORM behavior)
            if room.code != self.room_code:
                print("Room code is invalid")
                return

            response_is_banned = isBanned(user=self.user, room=room)

            # user is banned of the room
            if response_is_banned is True:
                print("User is banned from the room")
                return

            max_connections = room.people_amount

            async_to_sync(self.channel_layer.group_add)(
                self.room_code,
                self.channel_name
            )

            # room capacity exceded
            if len(self.channel_layer.groups[self.room_code]) > max_connections:
                return

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

    def disconnect(self, close_code):

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

        async_to_sync(self.channel_layer.group_discard)(
            self.room_code,
            self.channel_name
        )

        self.close()

    def delete_disconnect(self, data, close_code):

        print('disconnecting ', data.user, ' from ', data.code_room_conected)

        if data.code_room_conected in self.channel_layer.groups:
            async_to_sync(self.channel_layer.group_discard)(
                data.code_room_conected,
                data.channel_name_connected
            )

        updateConnection(
            user=data.user, channel_name="", code_room="", state=False)

    def receive(self, text_data):

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
                print("Room does not exists")
                return

            room_user_id = getRoom(
                room_code=connection_data['connected_room_code']).user.id

            if self.user.id != room_user_id:
                print("User tried to delete a room that he does not own")
                return

            connection_data, users_connected = deleteRoom(user=self.user)

            for user_con in users_connected:
                self.delete_disconnect(
                    close_code=1000, data=user_con)

            updateRoomInstances(user=self.user)
            self.close()

        # chat message
        else:
            if isConnected(self.user)['state'] is False:
                return

            if getRoom(room_code=connection['connected_room_code']) is None:
                return

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

        message = event['message']
        username = event['username']
        isUser = self.user.username == username

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username,
            'isUser': isUser
        }))

    def room_code_message(self, event):

        self.send(text_data=json.dumps({
            'type': 'room_created',
            'room_code': self.room_code,
            'room_name': self.room_name
        }))
        # close connection after creating room
        self.create_disconnect(close_code=1000)

    def join_request(self):
        message = 'El usuario ' + self.user.username + ' quiere entrar a la sala'
        self.send(text_data=json.dumps({
            'type': 'join_request',
            'message': message
        }))

    def get_user(self, scope):

        user = None
        if scope['user'].is_authenticated:
            user = scope['user']
        return user
