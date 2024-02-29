import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .serializers import CardRoundSerializer
from .services.game_fool import GameFool


#
# @login_required
# def lobby(request):
#     if request.GET.get("create_new_room") and Round.objects.count() < 20:
#         new_room = Round.objects.create(is_complete=True)
#         new_room.add_player()
#         new_room.add_player()
#         new_room.add_player()
#     rooms = Round.objects.all().order_by("pk")
#     return render(request, 'pole_chudes/lobby.html', {"rooms": rooms})


@login_required
def fool(request, pk):
    # if Card.objects.all().count() == 0:
    #     Card.create_deck()   # Для первого запуска
    full_deck = bool(request.GET.get("full_deck", False))
    # game: Round = get_object_or_404(Round, pk=pk)
    # p2 = int(request.GET.get("p2", 0))
    # p3 = int(request.GET.get("p3", 0))
    # if request.GET.get("start_new_game"):
    #     return render(request, 'card_games/fool_game.html',
    #                   fool_game.start_new_game(game, users_id=[request.user.id, p2, p3],
    #                                            creator=request.user, is_one_device=is_one_device))
    # else:
    #     return render(request, 'card_games/fool_game.html',
    #                   fool_game.start_game(game, users_id=[request.user.id, p2, p3],
    #                                        creator=request.user, is_one_device=is_one_device))

    fool_game = GameFool(pk, full_deck)
    #
    # player1 = Player(User(id=1))
    # player2 = Player(player_id=2)
    # player3 = Player(player_id=3)
    #
    # fool_game.game.add_player(player1)
    # fool_game.game.add_player(player2)
    # fool_game.game.add_player(player3)

    fool_game.start_game()

    return render(request, 'card_games/game_fool.html', {'game': CardRoundSerializer(fool_game.game).data})


def response_json(data):
    return HttpResponse(json.dumps(data), content_type='application/json')
