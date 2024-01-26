from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def lobby(request):

    if request.method == "POST":

        response_data = {
            'success': True
        }

        return JsonResponse(response_data)

    return render(request, 'index.html')
