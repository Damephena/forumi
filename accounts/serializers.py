from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import UserProfile

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    """Override default token login to include `user` data"""
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "id": self.user.id,
            "email": self.user.email,
            "is_verified": self.user.is_verified,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser
        })

        return data


class UserProfileSerializer(serializers.ModelSerializer):

    """User Profile Serializer"""
    class Meta:
        model = UserProfile
        fields = "__all__"


class CreateUserSerializer(serializers.ModelSerializer):

    """Serializer to create a new user."""
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "is_active": {"read_only": True},
            "is_verified": {"read_only": True},
            "password": {"write_only": True},
            "user_permissions": {"read_only": True},
            "last_login": {"read_only": True},
            "date_joined": {"read_only": True},
            "groups": {"read_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
        }

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_user(email, password, **validated_data)

        user_profile = UserProfile.objects.create(user=user)
        return user

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return UserProfileSerializer(profile, many=False).data
        except:
            return None


class  RetrieveUserSerializer(serializers.ModelSerializer):

    """Serializer to retrieve existing user"""
    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return UserProfileSerializer(profile, many=False).data
        except:
            return None

    class Meta:
        model = User
        exclude = ["password", "date_joined",]
        depth = 1


class UpdateUserSerializer(serializers.ModelSerializer):

    """Serializer to Update User Data"""
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]
