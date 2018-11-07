'''articles/serializers'''
from rest_framework import serializers
# django.forms.fields.ImageField

from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    description = serializers.CharField()
    slug = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=25), min_length=None, max_length=None, required=False)
    time_to_read = serializers.IntegerField(required=False)
    time_created = serializers.SerializerMethodField()
    time_updated = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()

    # TODO: handle images
    
    class Meta:
        model = Article
        fields = ('title', 'body', 'description', 'slug', 'tags',
                  'time_to_read', 'author', 'time_created', 'time_updated','favorited')

    def get_time_created(self, instance):
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        return instance.time_updated.isoformat()

    def create(self, validated_data):
        return Article.objects.create(**validated_data)
    
    def  update(self, instance, validated_data):
        pass

    def get_favorited(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.profile.favorited(instance)
