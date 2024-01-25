from django.shortcuts import render
from django.http import JsonResponse


def lobby(request):

    if request.method == "POST":

        response_data = {
            'success': True
        }

        return JsonResponse(response_data)

    return render(request, 'index.html')
