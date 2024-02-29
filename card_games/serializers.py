from rest_framework import serializers

from .models import CardRound, CardPlayer, Deck, Card, Table, User


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "is_superuser", "is_staff", "avatar"]

    def get_avatar(self, user: User):
        if user.userprofile.avatar:
            return user.userprofile.avatar.url
        else:
            return '/static/svg/avatar.svg'


class CardSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ["suit", "rank", "fullname"]

    def get_fullname(self, card: Card):
        return str(card)


# class DeckSerializer(serializers.ModelSerializer):
#     cards = CardSerializer(many=True, read_only=True)
#     last = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Deck
#         fields = ["cards", "last"]
#
#     def get_last(self, deck: Deck):
#         return CardSerializer(deck.cards.last()).data

class DeckSerializer(serializers.ModelSerializer):
    last = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ["cards", "last"]

    def get_last(self, deck: Deck):
        return CardSerializer(deck.cards[-1]).data


class TableSerializer(serializers.ModelSerializer):
    attacking_cards = CardSerializer(many=True, read_only=True)
    defending_cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = ["attacking_cards", "defending_cards"]


class CardPlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    hand = CardSerializer(many=True, read_only=True)

    class Meta:
        model = CardPlayer
        fields = ["id", "user", "hand", "in_game"]


class CardRoundSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    deck = DeckSerializer()
    # table = TableSerializer()
    players = serializers.SerializerMethodField()

    class Meta:
        model = CardRound
        fields = ["pk", "creator", "deck", "trump", "is_complete", "game", "parameters", "bet",
                  "players_count", "players", "attacking_player_index", "defending_player_index", "comment",
                  "change_at"]  # "table",
        depth = 3

    def get_players(self, obj: CardRound):
        players = obj.players.order_by('pk').all()[:obj.players_count + 1]
        if len(players):
            return CardPlayerSerializer(players, many=True).data
        else:
            return None
