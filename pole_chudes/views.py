import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, get_object_or_404

from chat.models import Room
from .service import pole_chudes_game


def lobby(request, pk=1):
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
    if checked_letter := request.GET.get("checked_letter"):
        if checked_letter == "+":
            data = pole_chudes_game.open_first_hidden_letter(pk)
        else:
            data = pole_chudes_game.check_letter(checked_letter, pk)
        return HttpResponse(json.dumps(data), content_type='application/json')
    elif full_word := request.GET.get("full_word"):
        return HttpResponse(json.dumps(pole_chudes_game.check_full_word(full_word, pk)),
                            content_type='application/json')
    elif request.GET.get("start_new_game"):
        return render(request, 'pole_chudes/game.html', pole_chudes_game.start_new_game(pk))
    else:
        return render(request, 'pole_chudes/game.html', pole_chudes_game.start_game(pk))


@login_required
def room(request, pk):
    chat_room: Room = get_object_or_404(Room, pk=pk)
    return render(request, 'chat/room.html', {
        "room": chat_room,
        "room_name": chat_room.name,
        "session_key": request.session.session_key,
    })
