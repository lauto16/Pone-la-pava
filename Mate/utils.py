from chat.models import Room


def createRoomRegister(name, code, user_name, people_amount):
    try:
        Room.objects.create(name=name, code=code,
                            user_name=user_name, people_amount=people_amount)
        return True
    except:
        return False
