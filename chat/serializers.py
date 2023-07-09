from rest_framework import serializers

from .models import User, Room, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "is_superuser", "is_staff"]
        # exclude = ["email", "password", "user_permissions"]

    # class UserSerializer(serializers.ModelSerializer):
    #     class Meta:
    #         model = User
    #         fields = ["id", "username", "email", "password"]
    #         extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Message
        exclude = []
        depth = 1


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    # messages = MessageSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    host = UserSerializer()
    current_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["pk", "name", "host", "messages", "current_users", "last_message"]
        depth = 1
        read_only_fields = ["messages", "last_message"]

    def get_last_message(self, obj: Room):
        return MessageSerializer(obj.messages.order_by('created_at').last()).data

    def get_messages(self, obj: Room):
        # Получение последних 20 сообщений для комнаты
        latest_messages = obj.messages.order_by('-created_at')[:100:-1]
        serializer = MessageSerializer(latest_messages, many=True)
        return serializer.data
