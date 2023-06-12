from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import TetrisScore


def games(request):
    return render(request, 'games/games.html')


@login_required
def tetris(request):
    if request.GET.get('score') and request.GET.get('lines') and request.GET.get('level'):
        tetris_score = TetrisScore.create(request)
        tetris_score.save()
        return HttpResponse("OK")
    else:
        return render(request, 'games/tetris.html')


def tetris_results(request):
    sorted_game_scores = TetrisScore.objects.order_by('-score')[:40]
    context = {
        'tetris_scores': sorted_game_scores,
    }
    return render(request, 'games/tetris_results.html', context)
