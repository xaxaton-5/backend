from rest_framework import serializers

from messaging.models import ChatMessage


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'text', 'from_user', 'sent_date', 'update_date')
