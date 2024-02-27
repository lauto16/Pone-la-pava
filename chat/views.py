from Mate.utils import getUser, getRooms, getRoomUsers, updateRoomInstances, getMessages, isConnected, isRoomOwner
from django.shortcuts import render, redirect
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

            isOwner = isRoomOwner(rooms=rooms, room_code=room_code)

            response_data = {
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
                'room_connected_users': room_usernames
            }

            return JsonResponse(response_data)

        elif action == 'logout':
            logout(request)

            response = {
                'success': True
            }
            return JsonResponse(response)

        elif action == 'banUser':
            username = data.get('username')
            # ban user
            return JsonResponse({'success': True})

    return render(request, 'index.html', {'rooms': rooms})
