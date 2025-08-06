import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render

from .models import GameScore
from .services import guess_the_word_game, find_word_at_mask
from .services.timer import elapsed_time, start_timer


@login_required
def process_input(request):
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
                'dif': current_session.difficulty,
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
        if not current_session.entered_words_list and elapsed_time(current_session.start_time) > 100:
            current_session.start_time = start_timer()
        # guess_the_word_game.start_new_game(current_session)
        entered_colored_words_list = []
        if current_session.entered_words_list:
            entered_colored_words_list = guess_the_word_game.word_list_coloring(
                current_session.entered_words_list,
                current_session.coincidences_list)
        context = {'notice': current_session.notice,
                   'dif': current_session.difficulty,
                   'show_rules': ('hide', 'show')[not entered_colored_words_list],
                   'entered_colored_words_list': entered_colored_words_list,
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
    sorted_game_scores = GameScore.objects.filter(difficulty=difficulty).order_by('attempts', 'elapsed_time')[:40]

    context = {
        'game_scores': sorted_game_scores,
        'dif': difficulty
    }

    return render(request, 'guess_the_word_game/results.html', context)


@user_passes_test(lambda u: u.groups.filter(name='Testers').exists())
def remove(request):
    if word := request.GET.get('remove_word'):
        return HttpResponse(guess_the_word_game.remove_line_with_word(word))
    elif difficulty := request.GET.get('dif'):
        random_noun = guess_the_word_game.get_random_noun(int(difficulty))
        meaning = guess_the_word_game.get_full_meaning_word(random_noun)
        data = {'noun': random_noun, 'meaning': meaning}
        return HttpResponse(json.dumps(data), content_type='application/json')
    elif word := request.GET.get('get_mean'):
        word = word.strip().lower().replace("ё", "е")
        if guess_the_word_game.is_there_a_word_meaning(word):
            meaning = guess_the_word_game.get_full_meaning_word(word)
        else:
            meaning = f'Значение слова "{word}" не найденов словаре'
        data = {'noun': word, 'meaning': meaning}
        return HttpResponse(json.dumps(data), content_type='application/json')

    return render(request, 'guess_the_word_game/remove_word.html')


@user_passes_test(lambda u: u.is_superuser)
def helper(request):
    matches = [" "]
    wrong_words = []
    frequent_words = ["океан", "спорт", "спирт", "фильм", "выгул"]
    letters = request.GET.get('letters', '').lower()
    excluded_letters = request.GET.get('excluded_letters', '').lower()
    pattern = request.GET.get('pattern', '*****').lower()
    if excluded_letters or letters:
        words = find_word_at_mask.get_all_words_at_length(len(pattern))
        matches = find_word_at_mask.find_matches_with_conditions(pattern.lower(), words, letters, excluded_letters)
        if wrong_words := [word for word in request.GET.get('wrong_words', '').lower().split(',')
                           if len(word) == len(pattern)]:
            matches = find_word_at_mask.filter_words_by_letter_match(matches, pattern, wrong_words)

    return render(request, 'guess_the_word_game/helper.html',
                  {
                      'frequent_words': frequent_words,
                      'wrong_words': wrong_words,
                      'matches': matches,
                      'pattern': pattern,
                      'letters': letters,
                      'excluded_letters': excluded_letters
                  }
                  )
