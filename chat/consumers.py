import json
from Mate.utils import verifiedSocket
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from channels.exceptions import DenyConnection, StopConsumer
from channels.generic.websocket import WebsocketConsumer
from Mate.utils import createRoomRegister, roomExists, updateConnection, isConnected


class ChatConsumer(WebsocketConsumer):

    """
    connect: recibe 2 tipos de peticiones: 
        -create -> valida que todo el usuario cumpla los requerimientos
                   y que los argumentos de creacion sean correctos mediante 
                   verifiedSocket, crea una nueva room, la agrega a la BD

        -join -> valida que el usuario no se encuentre ya en una room, luego
        verifica que la room exista en la base de datos, agrega al usuario a la
        room y modifica el registro de Connected (donde se almacena la room en la
        que se encuentra el usuario)


    disconnect: obtiene los datos de la room actual mediante isConnected y cierra la conexion,
                luego resetea Connection y hace raise StopConsumer para detener la clase


    receive: recibe los datos del frontend, tiene 2 peticiones:
            - 'delete_socket' -> desconecta al usuario del socket
            - 'chat_message' -> recepcion y reenvio de mensajes al front  si el usuario esta 
                                conectado y el mensaje no esta vacio

    get_user: obtiene el usuario que envio la peticion

    """

    def connect(self):

        self.action = self.scope['url_route']['kwargs']['action']
        self.user = self.get_user(self.scope)
        self.room_code = 0

        if self.action == 'create':

            received_room_name = self.scope['url_route']['kwargs']['room_name_code']
            received_people_amount = self.scope['url_route']['kwargs']['people_amount']

            validator = verifiedSocket(
                user=self.user, people_amount=received_people_amount, room_name=received_room_name)

            if validator.output():

                self.room_code = validator.socket_code
                self.room_name = validator.room_name
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

                if not (response_oncreate):
                    raise DenyConnection

            else:
                raise DenyConnection

        if self.action == 'join':

            response_is_connected = isConnected(user=self.user)

            if response_is_connected['state'] == False:
                self.room_code = self.scope['url_route']['kwargs']['room_name_code']

                if roomExists(self.room_code):

                    async_to_sync(self.channel_layer.group_add)(
                        self.room_code,
                        self.channel_name
                    )

                    self.accept()

                    updateConnection(
                        user=self.user, channel_name=self.channel_name, code_room=self.room_code, state=True)

            else:
                return

    def disconnect(self, close_code):

        disconnect_data = isConnected(user=self.user)

        if disconnect_data['connected_room_code'] in self.channel_layer.groups:
            async_to_sync(self.channel_layer.group_discard)(
                disconnect_data['connected_room_code'],
                disconnect_data['connected_channel_name']
            )

        updateConnection(
            user=self.user, channel_name="", code_room="", state=False)

        raise StopConsumer

    def receive(self, text_data):

        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'delete_socket':
            self.disconnect(close_code=1000)

        else:
            if isConnected(self.user)['state'] == True:
                message = text_data_json['message']

                if len(message) < 1:
                    return

                connection = isConnected(user=self.user)

                async_to_sync(self.channel_layer.group_send)(
                    connection['connected_room_code'],
                    {
                        'type': 'chat_message',
                        'message': message
                    }
                )

    def chat_message(self, event):

        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    def get_user(self, scope):

        user = None
        if scope['user'].is_authenticated:
            user = scope['user']
        return user
