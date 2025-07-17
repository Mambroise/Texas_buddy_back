# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :community/serialiser.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from community.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'activity', 'event', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']