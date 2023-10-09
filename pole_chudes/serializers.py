from datetime import datetime, timedelta

from rest_framework import serializers

from .models import Round, Player, Riddle, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "is_superuser", "is_staff"]


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Player
        fields = ["id", "user", "name", "score", "in_game"]


class RiddleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riddle
        fields = ["question"]
        depth = 1


#
# class SystemMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SystemMessage
#         fields = ["action", "comment", "player_name"]


class RoundSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    riddle = RiddleSerializer()
    # players = PlayerSerializer(many=True, read_only=True)
    players = serializers.SerializerMethodField()
    is_old_game = serializers.SerializerMethodField()

    class Meta:
        model = Round
        fields = ["pk", "creator", "riddle", "word_mask", "is_complete", "wheel_angle", "wheel_sector", "is_one_device",
                  "checked_letters", "points_earned", "wait_to_spin", "players", "active_player_index", "comment",
                  "is_old_game"]
        depth = 3

    def get_players(self, obj):
        players = obj.players.order_by('pk').all()[:3]
        if len(players):
            return PlayerSerializer(players, many=True).data
        else:
            return None

    def get_is_old_game(self, obj):
        return datetime.now(obj.change_at.tzinfo) - obj.change_at > timedelta(minutes=20)
