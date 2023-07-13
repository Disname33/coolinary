from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404

from .models import Room


def index(request):
    if request.method == "POST":
        if name := request.POST.get("name"):
            name = ' '.join(name.strip().split())
            name = name[0].upper() + name[1:]
            chat_room = None
            try:
                chat_room = Room.objects.get(name=name)
            except Exception as e:
                print(e)
            if not chat_room:
                chat_room = Room.objects.create(name=name, host=request.user)
            return HttpResponseRedirect(reverse("room", kwargs={"pk": chat_room.pk}))
    return render(request, 'chat/index.html')


@login_required
def room(request, pk):
    chat_room: Room = get_object_or_404(Room, pk=pk)
    return render(request, 'chat/room.html', {
        "room": chat_room,
        "room_name": chat_room.name,
        "session_key": request.session.session_key,
    })
