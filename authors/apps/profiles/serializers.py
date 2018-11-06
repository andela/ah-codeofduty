from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for creating a profile"""
    username = serializers.CharField(source='user.username')
    surname = serializers.CharField(allow_blank=True, required=False, min_length=1, max_length=50)
    last_name = serializers.CharField(allow_blank=True, required=False, min_length=1, max_length=50)
    avatar = serializers.URLField()
    bio = serializers.CharField(allow_blank=True, required=False, min_length=5, max_length=255)
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'surname', 'last_name', 'avatar', 'bio', 'created_at',
                  'modified_at', 'following']

    def get_following(self, instance):
        request = self.context.get('request', None)

        if not request.user.is_authenticated:
            return False

        follower = request.user.profile
        followee = instance
        return follower.is_following(followee)

