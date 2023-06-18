from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import TetrisScore, MatchThreeScore


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


def match_three(request):
    if request.GET.get('score') and request.GET.get('level'):
        if request.user.is_authenticated:
            match_three_score = MatchThreeScore.create(request)
            match_three_score.save()
            return HttpResponse("OK")
        else:
            return HttpResponse("ERROR")
    else:
        return render(request, 'games/match_three.html')


def match_three_results(request):
    sorted_game_scores = MatchThreeScore.objects.order_by('-level')[:40]
    context = {
        'match_three_scores': sorted_game_scores,
    }
    return render(request, 'games/match_three_results.html', context)
