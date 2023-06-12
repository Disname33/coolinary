from django.shortcuts import render
from django.http import HttpResponse
from .services import guess_the_word_game
from django.contrib.auth.decorators import login_required
from .services.timer import elapsed_time, start_timer
from .models import GameScore


@login_required
def process_input(request):
    # agent = request.META.get('HTTP_USER_AGENT')
    current_session = guess_the_word_game.get_current_session(request.user)
    if entered_string := request.GET.get('my_input'):
        # Получение значения из поля input
        entered_string = entered_string.strip().lower().replace("ё", "е")
        if guess_the_word_game.input_validation(entered_string, current_session):
            guess_the_word_game.input_cycle(entered_string, current_session)
            the_end = False
            if is_win := guess_the_word_game.is_win(entered_string, current_session):
                current_session.notice = guess_the_word_game.notice_congratulations_final(current_session)
                game_score = GameScore.copy_of_current_session(current_session)
                game_score.save()
            elif the_end := guess_the_word_game.is_loss(current_session):
                current_session.notice = guess_the_word_game.notice_loss(current_session)
            entered_colored_words_list = guess_the_word_game.word_list_coloring(
                current_session.entered_words_list,
                current_session.coincidences_list)
            context = {
                'entered_colored_words_list': entered_colored_words_list,
                'notice': current_session.notice,
                'dif': current_session.difficulty,
                'firework': ('none', 'visible')[is_win],
                'remaining_attempts': guess_the_word_game.remaining_attempts(current_session)
            }
            if is_win or the_end:
                guess_the_word_game.start_new_game(current_session)
            current_session.save()
            return render(request, 'guess_the_word_game/enter_words.html', context)
        else:
            entered_colored_words_list = guess_the_word_game.word_list_coloring(
                current_session.entered_words_list,
                current_session.coincidences_list)
            context = {
                'entered_colored_words_list': entered_colored_words_list,
                'notice': current_session.notice,
                'firework': 'none',
                'remaining_attempts': guess_the_word_game.remaining_attempts(current_session),
            }
            return render(request, 'guess_the_word_game/enter_words.html', context)
    elif difficulty := request.GET.get('dif'):
        current_session.difficulty = int(difficulty)
        guess_the_word_game.start_new_game(current_session)
        print(current_session.hidden_word)
        context = {'notice': current_session.notice,
                   'dif': current_session.difficulty,
                   'show_rules': 'show',
                   'firework': 'none',
                   'remaining_attempts': guess_the_word_game.remaining_attempts(current_session)
                   }
        current_session.save()
        return render(request, 'guess_the_word_game/enter_words.html', context)
    else:
        print("Первоначальная загрузка игры")
        if len(current_session.entered_words_list) and elapsed_time(current_session.start_time) > 100:
            current_session.start_time = start_timer()
        # guess_the_word_game.start_new_game(current_session)
        context = {'notice': current_session.notice,
                   'dif': current_session.difficulty,
                   'show_rules': 'show',
                   'firework': 'none',
                   'remaining_attempts': guess_the_word_game.remaining_attempts(current_session)
                   }
        current_session.save()
        return render(request, 'guess_the_word_game/enter_words.html', context)


def results(request):
    if word := request.GET.get('need_mean'):
        return HttpResponse(guess_the_word_game.get_full_meaning_word(word))

    if difficulty := request.GET.get('dif'):
        print(difficulty)
    else:
        difficulty = guess_the_word_game.get_current_session(request.user).difficulty
    sorted_game_scores = GameScore.objects.filter(difficulty=difficulty).order_by('attempts', 'score')[:40]

    context = {
        'game_scores': sorted_game_scores,
        'dif': difficulty
    }

    return render(request, 'guess_the_word_game/results.html', context)
