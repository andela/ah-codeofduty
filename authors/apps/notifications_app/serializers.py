"""
Notification serializer module
"""

from notifications.models import Notification

from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer class
    """
    class Meta:
        """
        Meta class for notification serializer
        """
        model = Notification

        fields = (
            'id', 'verb', 'target', 'level',
            'timestamp', 'description', 'recipient')