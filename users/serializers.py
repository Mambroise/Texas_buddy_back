# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/serialiser.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models.user import User
from activities.models import Category
from django.contrib.auth.password_validation import validate_password


#  User create
class UserSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 'country',
            'sign_up_number', 'first_ip', 'second_ip',
            'interests'
        ]



# ask django to create new sign_up_number and send it in an email
class ResendRegistrationNumberSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RegistrationVerificationSerializer(serializers.Serializer):
    sign_up_number = serializers.CharField()
    email = serializers.EmailField()


class TwoFACodeVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserInterestsUpdateSerializer(serializers.ModelSerializer):
    # Accepter une liste d’IDs de catégories depuis le front
    interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ['interests']

    def update(self, instance, validated_data):
        if 'interests' in validated_data:
            instance.interests.set(validated_data['interests'])
            instance.save()
        return instance
