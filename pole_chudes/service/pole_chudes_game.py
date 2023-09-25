from ..models import Round


def check_letter(letter, pk):
    game = Round.objects.get(pk=pk)
    checked_letter = letter.strip().upper()[0]
    if checked_letter not in game.word_mask.upper():
        indices = [i for i, letter in enumerate(game.riddle.word.upper()) if letter == checked_letter]
        if indices:
            word_list = list(game.word_mask.upper())
            for index in indices:
                word_list[index] = checked_letter
            game.word_mask = "".join(word_list)
            if "*" not in game.word_mask:
                game.is_complete = True
            game.save()
            return {'word_mask': game.word_mask, 'is_complete': game.is_complete, 'letter_count': len(indices)}
        else:
            return {'comment': "Нет такой буквы", 'is_complete': game.is_complete}
    else:
        return {'comment': "Букву уже отгадали", 'is_complete': game.is_complete}


def open_first_hidden_letter(pk):
    game = Round.objects.get(pk=pk)
    letter = game.riddle.word[game.word_mask.find("*")]
    return check_letter(letter, pk)


def check_full_word(full_word, pk):
    game = Round.objects.get(pk=pk)
    if full_word.upper() == game.riddle.word.upper():
        game.word_mask = game.riddle.word
        game.is_complete = True
        game.save()
        return {'word_mask': game.word_mask.upper(), 'comment': "Вы победили!",
                'is_complete': game.is_complete}
    else:
        return {'comment': "Вы проиграли", 'is_complete': game.is_complete}


def start_game(pk):
    game = Round.objects.filter(pk=pk).first()
    if game and game.is_complete:
        game.next_riddle()
    else:
        # Первый запуск игры. Создание трёх игровых комнат.
        for _ in range(3):
            Round().save()
        game = Round.objects.get(pk=pk)
    return {"word_mask": game.word_mask.upper(), "question": game.riddle.question}
