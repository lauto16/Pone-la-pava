import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        # nombre de la sala
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # añadir al usuario (channel_layer) a el grupo
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,

            # nombre del canal, se crea automatico para cada user
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):

        # Salir del grupo de la sala
        self.channel_layer.group_discard(

            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # enviar el mensaje a todos los users que se encuentren
        # en la room

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
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
