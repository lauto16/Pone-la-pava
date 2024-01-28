from Mate.utils import getUser, getRooms
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json


@login_required
def lobby(request):

    user = getUser(request)
    rooms = getRooms(user)

    if request.method == 'POST':

        body_unicode = request.body.decode('utf-8')
        room_name = json.loads(body_unicode)

        return JsonResponse({'room_name': room_name})

    return render(request, 'index.html', {'rooms': rooms})
