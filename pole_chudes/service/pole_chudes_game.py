import random

from ..models import Round
from ..serializers import RoundSerializer


class Wheel:
    sectors = ("200", "X3", "700", "Банкрот", "1000", "100", "X2", "600", "800", "+", "400", "900", "0", "Приз", "500",
               "300")
    scores = (200, 0, 700, 0, 1000, 100, 0, 600, 800, 0, 400, 900, 0, 1200, 500, 300)
    sector = sectors[0]
    score = scores[0]
    angle = 0

    def __init__(self, angle=None):
        if angle is None:
            self.angle = random.randint(0, 359)
        else:
            self.angle = angle
        index = int((self.angle - 11) % 360 / 22.5)
        self.sector = self.sectors[index]
        self.score = self.scores[index]


def rotate_wheel(game: Round):
    if game.wait_to_spin:
        active_player = game.get_active_player()
        wheel = Wheel()
        game.wheel_angle = wheel.angle
        game.wheel_sector = wheel.sector
        game.points_earned = wheel.score
        game.comment = None
        game.wait_to_spin = False
        match wheel.sector:
            case 'Банкрот':
                game.set_active_player(score=0)
                game.next_player(f'Игрок{game.active_player_index + 1} банкрот')
            case '0':
                game.next_player('Переход хода')
            case 'X2':
                game.points_earned = active_player.score
            case 'X3':
                game.points_earned = active_player.score * 2
            case '+':
                return open_first_hidden_letter(game)
            case 'Приз':
                return open_first_hidden_letter(game)
        game.save()
        return RoundSerializer(game).data
    else:
        game.comment = 'Назовите букву!'
        return RoundSerializer(game).data


def check_letter(letter: str, game: Round):
    if game.wait_to_spin:
        game.comment = 'Вращайте барабан!'
        return RoundSerializer(game).data
    else:
        checked_letter = letter.strip().upper()[0]
        if checked_letter in game.word_mask.upper():
            game.next_player("Букву уже отгадали")
            return RoundSerializer(game).data
        else:
            indices = [i for i, letter in enumerate(game.riddle.word.upper()) if letter == checked_letter]
            if indices:
                game.wait_to_spin = True
                game.comment = None
                word_list = list(game.word_mask.upper())
                game.set_active_player(add_score=game.points_earned * len(indices))
                for index in indices:
                    word_list[index] = checked_letter
                game.word_mask = "".join(word_list)
                if "*" not in game.word_mask:
                    game.win()
                game.save()
                return RoundSerializer(game).data
            else:
                game.next_player("Нет такой буквы")
                return RoundSerializer(game).data


def open_first_hidden_letter(game: Round):
    letter = game.riddle.word[game.word_mask.find("*")]
    return check_letter(letter, game)


def check_full_word(full_word: str, game: Round):
    full_word = full_word.strip().upper().replace('Ё', 'Е')
    if full_word == game.riddle.word.upper():
        game.word_mask = game.riddle.word
        game.is_complete = True
        game.win()
        game.save()
        return RoundSerializer(game).data
    else:
        game.set_active_player(in_game=False)
        game.next_player(f"Игрок{game.active_player_index + 1} проиграл и покидает игру")
        return RoundSerializer(game).data


def start_game(game: Round):
    if game and game.is_complete:
        game.next_riddle()
    return RoundSerializer(game).data


def start_new_game(game: Round):
    game.next_riddle()
    return RoundSerializer(game).data
