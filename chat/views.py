from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def chat(request):
    return render(request, "chat/index.html")


@login_required
def room(request, room_name):
    if room_name.startswith("pm_"):
        user_list = room_name.split("_")[1:]
        if str(request.user) in user_list:
            users = ', '.join(user_list[:-1]) + (' и ' if len(user_list) > 1 else '') + user_list[-1]
            return render(request, "chat/room.html", {"room_name": room_name, "personal_message": True, "users": users})
        else:
            return render(request, "chat/room.html", {"alien": True})
    else:
        return render(request, "chat/room.html", {"room_name": room_name})
