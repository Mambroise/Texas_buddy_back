# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/serialiser.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models.user import User
from django.contrib.auth.password_validation import validate_password

#  User create
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'country', 'sign_up_number']

    def create(self, validated_data):
        email = validated_data.get('email', None)
        if not email:
            raise serializers.ValidationError("L'email est requis pour générer le nom d'utilisateur.")
        
        validated_data['username'] = email
        return super().create(validated_data)

# ask django to create new sign_up_number and send it in an emil
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