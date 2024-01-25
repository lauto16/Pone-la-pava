from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    people_amount = models.IntegerField()
