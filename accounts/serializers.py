from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserFollow
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url']

    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        # Placeholder for avatar URL - can be extended with a profile model
        return None


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='follower')
    followedAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserFollow
        fields = ['user', 'followedAt']


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='following')
    followedAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserFollow
        fields = ['user', 'followedAt']


class UserSuggestionSerializer(serializers.ModelSerializer):
    mutualFriends = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mutualFriends']
        avatar_url = 'https://avatars.dicebear.com/api/human/{id}.svg'

    def get_mutualFriends(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        user_following = set(
            request.user.following.values_list('following_id', flat=True))
        obj_following = set(obj.following.values_list(
            'following_id', flat=True))
        return len(user_following.intersection(obj_following))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            return user
        raise serializers.ValidationError("Invalid credentials")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError(
                "New password cannot be the same as old password")
        return data


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
