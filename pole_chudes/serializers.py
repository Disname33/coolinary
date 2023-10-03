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
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Round
        fields = ["pk", "creator", "riddle", "word_mask", "is_complete", "wheel_angle", "wheel_sector", "is_one_device",
                  "checked_letters", "points_earned", "wait_to_spin", "players", "active_player_index", "comment"]
        depth = 3
