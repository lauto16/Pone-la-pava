from Mate.utils import (
    getUser,
    getRooms,
    updateRoomInstances,
    getConnected,
    roomRedirection,
    logoutUser,
    banUser
)
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@login_required
def lobby(request):
    """
    Is main view, it handles room redirections, connected users requests, logout and user bans

    Args:
        request (Web request): A request from the user containing data about request method, request data, etc

    Returns:
        JsonResponse: A JsonResponse that contains data the user requested
        render: A render containing the basic html template and the user rooms data
    """

    user = getUser(request)
    updateRoomInstances(user)
    rooms = getRooms(user)

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data['action']

        if action == 'redirectRoom':
            response_data = roomRedirection(
                data=data,
                user=user,
                rooms=rooms
            )
            return JsonResponse(response_data)

        elif action == 'getConnectedUsers':
            response_data = getConnected(
                user=user, rooms=rooms, get_connected=False)
            return JsonResponse(response_data)

        elif action == 'logout':
            response_data = logoutUser(request)
            return JsonResponse(response_data)

        elif action == 'banUser':
            response_data = banUser(
                user=user,
                rooms=rooms,
                data=data
            )
            return JsonResponse(response_data)

    return render(request, 'index.html', {'rooms': rooms})
