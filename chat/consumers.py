import json
from asgiref.sync import async_to_sync
from Mate.utils import createRoomRegister
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"chat_{self.room_code}"

        if hasattr(self, 'room_group_name'):
            self.disconnect(3001)

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
        user_name = text_data_json['user_name']
        room_name = text_data_json['room_name']
        room_code = text_data_json['room_code']
        people_amount = text_data_json['people_amount']

        if int(people_amount) > 15:
            people_amount = 15

        createRoomRegister(name=room_name, code=room_code,
                           user_name=user_name, people_amount=int(people_amount))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json
            }
        )

    def chat_message(self, event):

        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))
