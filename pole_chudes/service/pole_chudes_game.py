import random

from ..models import Round
from ..serializers import RoundSerializer


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# import time


class Wheel:
    sectors = ("200", "X3", "700", "Банкрот", "1000", "100", "X2",
               "600", "800", "+", "400", "900", "0", "Приз", "500", "300")
    scores = (200, 0, 700, 0, 1000, 100, 0, 600, 800, 0, 400, 900, 0, 1200, 500, 300)
    sector = sectors[0]
    score = scores[0]
    angle = 0

    def __init__(self, angle=None):
        if angle is None:
            self.angle = random.randint(0, 359)
        else:
            self.angle = angle
        index = int(self.angle % 360 / 22.5)
        self.sector = self.sectors[index]
        self.score = self.scores[index]


#
# @receiver(post_save, sender=Round)
# def bot_info(sender, instance, created, **kwargs):
#
#     def find_first_unique_char(checked_letters: str):
#         letters = 'ОЕАИНТСРВЛКМДПУЯЫЬГЗБЧЙХЖШЮЦЩЭФЪ'
#         for letter in letters:
#             if letter not in checked_letters:
#                 return letter
#         return random.choice(letters)
#
#     if instance.get_active_player().user is None and not instance.is_complete:
#         sys_msg = SystemMessage.objects.get_or_create(round=instance)[0]
#         time.sleep(0.5)
#         bot_name = instance.get_active_player().name,
#         if instance.wait_to_spin:
#             if instance.word_mask.count('*') == 1:
#                 sys_msg.action = 'check_full_word'
#                 sys_msg.comment = instance.riddle.word
#                 # check_full_word(instance.riddle.word, instance)
#             else:
#                 sys_msg.action = 'rotate_wheel'
#                 # rotate_wheel(instance)
#                 # time.sleep(4)
#         else:
#             sys_msg.action = 'check_letter'
#             sys_msg.comment = find_first_unique_char(instance.checked_letters)
#             # check_letter(find_first_unique_char(instance.checked_letters), instance)
#         sys_msg.save()
#
#
# @receiver(post_save, sender=SystemMessage)
# def bot_action(sender, instance, created, **kwargs):
#     game: Round = instance.round
#     time.sleep(1)
#     match instance.action:
#         case 'rotate_wheel':
#             time.sleep(2)
#             rotate_wheel(game)
#         case 'check_letter':
#             check_letter(instance.comment, game)
#         case 'check_full_word':
#             check_full_word(instance.comment, game)


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
                game.next_player(f'{game.get_active_player().name} - банкрот', save=False)
            case '0':
                game.next_player('Переход хода', save=False)
            case 'X2':
                game.points_earned = active_player.score
            case 'X3':
                game.points_earned = active_player.score * 2
            case '+':
                open_first_hidden_letter(game)
                return
            case 'Приз':
                open_first_hidden_letter(game, comment='Сектор "Приз" на барабане!')
                return
        game.save()
        # return RoundSerializer(game).data
    else:
        game.comment = 'Назовите букву!'
        # return RoundSerializer(game).data


def check_letter(letter: str, game: Round, comment=None):
    if game.wait_to_spin:
        game.comment = 'Вращайте барабан!'
        return RoundSerializer(game).data
    else:
        checked_letter = letter.strip().upper()[0]
        if checked_letter in game.checked_letters:
            game.next_player("Букву уже называли")
            # return RoundSerializer(game).data
        else:
            game.checked_letters += checked_letter
            indices = [i for i, letter in enumerate(game.riddle.word.upper()) if letter == checked_letter]
            if indices:
                game.wait_to_spin = True
                game.comment = comment
                word_list = list(game.word_mask.upper())
                game.set_active_player(add_score=game.points_earned * len(indices))
                for index in indices:
                    word_list[index] = checked_letter
                game.word_mask = "".join(word_list)
                if "*" not in game.word_mask:
                    game.win()
                game.save()
                # return RoundSerializer(game).data
            else:
                game.next_player("Нет такой буквы")
                # return RoundSerializer(game).data


def open_first_hidden_letter(game: Round, comment=None):
    letter_index = game.word_mask.find("*")
    letter = game.riddle.word[letter_index]
    if comment is None:
        comment = f'Откройте {letter_index + 1}-ю букву'
    return check_letter(letter, game, comment)


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
        game.next_player(f"{game.get_active_player().name} проиграл(а) и покидает игру")
        return RoundSerializer(game).data


def start_game(game: Round, users_id=list, creator=None, is_one_device=False):
    if game and (game.is_complete or is_old_game(game)):
        game.next_riddle(users_id=users_id, creator=creator, is_one_device=is_one_device)
    return RoundSerializer(game).data


def start_new_game(game: Round, users_id=list, creator=None, is_one_device=False):
    game.next_riddle(users_id=users_id, creator=creator, is_one_device=is_one_device)
    return RoundSerializer(game).data


def is_old_game(game: Round):
    from datetime import datetime, timedelta
    return datetime.now() - game.change_at > timedelta(minutes=20)
