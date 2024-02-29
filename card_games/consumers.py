import asyncio
import json

from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)

from .models import CardRound
from .serializers import CardRoundSerializer


class GameConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = CardRound.objects.all()
    serializer_class = CardRoundSerializer
    lookup_field = "pk"

    # async def websocket_connect(self, message):
    #     if self.scope['user'].is_authenticated:
    #         print(message)
    #         await super().websocket_connect(message)
    #     else:
    #         print(message)
    #         await self.close()

    # @model_observer(SystemMessage)
    # async def message_activity(self, message, observer=None, **kwargs):
    #     await self.send_json(message)
    #
    # @message_activity.groups_for_signal
    # def message_activity(self, instance: SystemMessage, **kwargs):
    #     yield f'room__{instance.round_id}'
    #     yield f'pk__{instance.pk}'
    #
    # @message_activity.groups_for_consumer
    # def message_activity(self, room=None, **kwargs):
    #     if room is not None:
    #         yield f'room__{room}'
    #
    # @message_activity.serializer
    # def message_activity(self, instance: SystemMessage, action, **kwargs):
    #     return dict(data=SystemMessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def send_group_message(self, message, message_action='info', sender='Ведущий'):
        # await self.channel_layer.group_add("your_group_name", self.channel_name)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'action': message_action,
                    "type": "group.message",
                    "message": message,
                    "sender": sender,
                }
            )

    async def group_message(self, event):
        if event["sender"] != self.scope["user"]:
            message = event["message"]
            message_action = event["action"]
            await self.send(text_data=json.dumps({"action": message_action, "data": message}))

    @action()
    async def join_room(self, pk, **kwargs):
        if self.scope['user'].is_authenticated:
            self.room_subscribe = pk
            await self.add_user_to_room(pk)

    # @action()
    # async def rename_player(self, name, player_id, **kwargs):
    #     room: CardRound = await CardRound.objects.aget(pk=self.room_subscribe)
    #     if players := await self.rename_player_db(name, player_id, room):
    #         await self.send_group_message({'players': players}, message_action='update_players')

    # @action()
    # async def bot_rotate_wheel(self, pk, **kwargs):
    #     room: Round = await Round.objects.aget(pk=self.room_subscribe)
    #     if self.user_is_active_player(room):
    #         await self.send_group_message({'rotate_wheel': 'rotate'})
    #         await database_sync_to_async(pole_chudes_game.rotate_wheel)(room)
    #
    # @action()
    # async def bot_next_letter(self, pk, name, **kwargs):
    #     room: Round = await Round.objects.aget(pk=self.room_subscribe)
    #     if self.is_creator_running_bot(room):
    #         if room.word_mask.count('*') == 1:
    #             full_word = await self.get_word(room)
    #             await self.send_group_message({'user': name, 'full_word': full_word})
    #             await database_sync_to_async(pole_chudes_game.check_full_word)(full_word, room)
    #         else:
    #             async def find_first_unique_char(checked_letters: str):
    #                 letters = 'ОЕАИНТСРВЛКМДПУЯЫЬГЗБЧЙХЖШЮЦЩЭФЪ'
    #                 for _letter in letters:
    #                     if _letter not in checked_letters:
    #                         return _letter
    #                 return random.choice(letters)
    #
    #             letter = await find_first_unique_char(room.checked_letters)
    #             await self.send_group_message({'user': name, 'letter': letter})
    #             await database_sync_to_async(pole_chudes_game.check_letter)(letter, room)
    #
    # @action()
    # async def rotate_wheel(self, pk, **kwargs):
    #     room: CardRound = await CardRound.objects.aget(pk=self.room_subscribe)
    #     if self.user_is_active_player(room):
    #         await self.send_group_message({'rotate_wheel': 'rotate'}, sender=self.scope["user"])
    #         await database_sync_to_async(pole_chudes_game.rotate_wheel)(room)
    #
    # @action()
    # async def check_letter(self, pk, letter, **kwargs):
    #     room: CardRound = await CardRound.objects.aget(pk=self.room_subscribe)
    #     if self.user_is_active_player(room):
    #         await self.send_group_message({'user': await self.get_active_player_name(pk), 'letter': letter})
    #         await database_sync_to_async(pole_chudes_game.check_letter)(letter, room)
    #
    # @action()
    # async def check_full_word(self, pk, full_word, **kwargs):
    #     room: CardRound = await CardRound.objects.aget(pk=self.room_subscribe)
    #     if self.user_is_active_player(room):
    #         await self.send_group_message({'user': await self.get_active_player_name(pk), 'full_word': full_word})
    #         await database_sync_to_async(pole_chudes_game.check_full_word)(full_word, room)
    #
    # @database_sync_to_async
    # def user_is_active_player(self, room: CardRound):
    #     return room.get_active_player().user == self.scope['user']
    #
    # @database_sync_to_async
    # def get_word(self, room: CardRound):
    #     return room.riddle.word
    #
    # @database_sync_to_async
    # def is_creator_running_bot(self, room: CardRound):
    #     return room.creator == self.scope['user'] and room.get_active_player().user is None
    #
    # @database_sync_to_async
    # def get_room(self, pk: int) -> CardRound:
    #     return CardRound.objects.get(pk=pk)
    #
    # @database_sync_to_async
    # def get_active_player_name(self, pk: int) -> str:
    #     return CardRound.objects.get(pk=pk).get_active_player().name
    #
    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: User = self.scope["user"]
        game = CardRound.objects.get(pk=pk)
        if not game.is_complete and not game.is_user_in_game(user):
            if game.take_vacant_seat(user) is None:
                asyncio.run(self.send_json({"action": action, "errors": "Нет свободных мест"}))
            # user.current_rooms.add(CardRound.objects.get(pk=pk))
    #
    # @database_sync_to_async
    # def rename_player_db(self, name, player_id, room: CardRound):
    #     player = room.players.get(pk=player_id)
    #     if player.user == self.scope["user"]:
    #         player.name = name
    #         player.save()
    #         return PlayerSerializer(room.players.order_by('pk').all()[:3], many=True).data
    #     else:
    #         return None
    #
    # async def send_if_errors(self, action, errors):
    #     if errors:
    #         await self.send_json({"action": action, "errors": errors})
