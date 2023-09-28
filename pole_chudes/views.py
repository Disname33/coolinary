import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Round
from .service import pole_chudes_game


@login_required
def lobby(request):
    if request.GET.get("create_new_room") and Round.objects.count() < 20:
        new_room = Round.objects.create(is_complete=True)
        new_room.add_player()
        new_room.add_player()
        new_room.add_player()
    rooms = Round.objects.all().order_by("pk")
    return render(request, 'pole_chudes/lobby.html', {"rooms": rooms})


@login_required
def room(request, pk):
    game: Round = get_object_or_404(Round, pk=pk)
    # return render(request, 'chat/room.html', {
    #     "room": chat_room,
    #     "room_name": chat_room.name,
    #     "session_key": request.session.session_key,
    # })
    if request.GET.get("rotate_wheel"):
        return response_json(pole_chudes_game.rotate_wheel(game))
    elif checked_letter := request.GET.get("checked_letter"):
        return response_json(pole_chudes_game.check_letter(checked_letter, game))
    elif full_word := request.GET.get("full_word"):
        return response_json(pole_chudes_game.check_full_word(full_word, game))
    elif request.GET.get("start_new_game"):
        return render(request, 'pole_chudes/game.html', pole_chudes_game.start_new_game(game))
    else:
        return render(request, 'pole_chudes/game.html', pole_chudes_game.start_game(game))


def response_json(data):
    return HttpResponse(json.dumps(data), content_type='application/json')
