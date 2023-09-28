from rest_framework import serializers

from .models import Round, Player, Riddle


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "score", "in_game"]


class RiddleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riddle
        fields = ["question"]
        depth = 1


class RoundSerializer(serializers.ModelSerializer):
    riddle = RiddleSerializer()
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Round
        fields = ["pk", "riddle", "word_mask", "is_complete", "wheel_angle", "wheel_sector", "points_earned",
                  "wait_to_spin", "players", "active_player_index", "comment"]
        depth = 2
