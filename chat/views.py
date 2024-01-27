from Mate.utils import getUser, updateConnection
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def lobby(request):

    user = getUser(request)

    updateConnection(
        user=user, channel_name="", code_room="", state=False)

    if request.method == "POST":

        response_data = {
            'success': True
        }

        return JsonResponse(response_data)

    return render(request, 'index.html')
