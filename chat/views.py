from Mate.utils import getUser, getRoom, getRooms, getRoomUsers, banRoomUser, updateRoomInstances, getMessages, isConnected, addMessage, isRoomOwner, updateConnection, getUserByName
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth import logout


@login_required
def lobby(request):

    user = getUser(request)
    updateRoomInstances(user)
    rooms = getRooms(user)

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data['action']

        if action == 'redirect_room':
            isOwner = False
            room_code = data.get('room_code')
            room_name = data.get('room_name')

            messages = getMessages(room_code=room_code, user=user)

            if messages is False:
                response_data = {
                    'success': False,
                    'error': 'No se pudo cargar los datos de la sala'
                }

                return JsonResponse(response_data)

            isOwner = isRoomOwner(rooms=rooms, room_code=room_code)

            response_data = {
                'success': True,
                'isOwner': isOwner,
                'room_code': room_code,
                'room_name': room_name,
                'room_messages': messages
            }

            return JsonResponse(response_data)

        elif action == 'getConnectedUsers':
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

            return JsonResponse(response_data)

        elif action == 'logout':
            logout(request)

            response = {
                'success': True
            }

            return JsonResponse(response)

        elif action == 'banUser':
            connection_data = isConnected(user=user)

            if connection_data['state'] is False:
                response_data = {
                    'success': False,
                    'error': 'No estas conectado a la sala'
                }
                return JsonResponse(response_data)

            room = getRoom(room_code=connection_data['connected_room_code'])

            if room is None:
                response_data = {
                    'success': False,
                    'error': 'La sala no existe'
                }
                return JsonResponse(response_data)

            if isRoomOwner(rooms=rooms, room_code=room.code) is False:
                response_data = {
                    'success': False,
                    'error': 'No eres el administrador de la sala'
                }
                return JsonResponse(response_data)

            username = data.get('username')

            # you cant ban yourself
            if username == user.username:
                response_data = {
                    'success': False,
                    'error': 'No puedes expulsarte a ti mismo'
                }
                return JsonResponse(response_data)

            response_ban_user = banRoomUser(username=username, room=room)

            if response_ban_user is False:
                response_data = {
                    'success': False,
                    'error': 'No se pudo expulsar al usuario de la sala'
                }
                return JsonResponse(response_data)

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

            return JsonResponse(response_data)

    return render(request, 'index.html', {'rooms': rooms})
