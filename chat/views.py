from django.shortcuts import render


def lobby(request):
    return render(request, 'index.html')
