from notifications.models import Notification

from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification

        fields = ('id', 'verb', 'target', 'level', 'timestamp', 'description', 'recipient')