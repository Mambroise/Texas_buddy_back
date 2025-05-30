# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/serialiser.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from django.contrib.auth.models import User  

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'country',"sign_up_number"]


class RegistrationVerificationSerializer(serializers.Serializer):
    registration_number = serializers.CharField()
    email = serializers.EmailField()


class TwoFACodeVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
