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
    p2 = int(request.GET.get("p2", 0))
    p3 = int(request.GET.get("p3", 0))
    is_one_device = request.GET.get("is_one_device", '0') == "1"
    if request.GET.get("start_new_game"):
        return render(request, 'pole_chudes/game.html',
                      pole_chudes_game.start_new_game(game, users_id=[request.user.id, p2, p3],
                                                      creator=request.user, is_one_device=is_one_device))
    else:
        return render(request, 'pole_chudes/game.html',
                      pole_chudes_game.start_game(game, users_id=[request.user.id, p2, p3],
                                                  creator=request.user, is_one_device=is_one_device))


def response_json(data):
    return HttpResponse(json.dumps(data), content_type='application/json')
