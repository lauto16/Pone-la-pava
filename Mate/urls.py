from Auth.views import *
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path('login/', login_view, name='login_view'),
    path('register/', register_view, name='register_view')
]
