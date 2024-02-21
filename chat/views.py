from Mate.utils import getUser, getRooms, updateRoomInstances, getMessages
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

            for room in rooms:
                if room_code == room.code:
                    isOwner = True
                    break

            response_data = {
                'isOwner': isOwner,
                'room_code': room_code,
                'room_name': room_name,
                'room_messages': messages
            }

            return JsonResponse(response_data)

        elif action == 'logout':
            logout(request)

            response = {
                'success': True
            }
            return JsonResponse(response)

    return render(request, 'index.html', {'rooms': rooms})
