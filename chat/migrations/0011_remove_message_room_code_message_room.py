# Generated by Django 5.0.1 on 2024-02-01 01:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_message_room_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room_code',
        ),
        migrations.AddField(
            model_name='message',
            name='room',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.room'),
            preserve_default=False,
        ),
    ]
