from rest_framework import serializers

from .models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for creating a profile"""
    username = serializers.CharField(source='user.username')
    surname = serializers.CharField(allow_blank=True, required=False, min_length=1, max_length=50)
    last_name = serializers.CharField(allow_blank=True, required=False, min_length=1, max_length=50)
    avatar = serializers.URLField()
    bio = serializers.CharField(allow_blank=True, required=False, min_length=5, max_length=255)
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'surname', 'last_name', 'avatar', 'bio', 'created_at',
                  'modified_at', 'followers', 'following']
