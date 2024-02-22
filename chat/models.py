from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    people_amount = models.IntegerField()


class RoomIntances(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_instances = models.IntegerField()


class Connected(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_connected = models.BooleanField()
    code_room_conected = models.CharField(
        max_length=100, null=True, blank=True)
    channel_name_connected = models.TextField(null=True, blank=True)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class AdmitedUser(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
