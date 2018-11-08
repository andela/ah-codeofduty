'''articles/serializers'''
from rest_framework import serializers
from django.utils.text import slugify
from authors.apps.authentication.serializers import UserSerializer
from ..authentication.models import User
from rest_framework.exceptions import PermissionDenied

from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    '''Article model serializer'''
    author = UserSerializer(read_only=True)
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(max_length=1000), min_length=None, max_length=None, required=False)
    description = serializers.CharField()
    slug = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=25), min_length=None, max_length=None, required=False)
    time_to_read = serializers.IntegerField(required=False)
    time_created = serializers.SerializerMethodField()
    time_updated = serializers.SerializerMethodField()

    class Meta:
        '''Class defining fields passed to database'''
        model = Article
        fields = ('title', 'body', 'images', 'description', 'slug', 'tags',
                  'time_to_read', 'author', 'time_created', 'time_updated')

    def get_time_created(self, instance):
        '''get time the article was created and return in iso format'''
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        '''get time the article was created and return in iso format'''
        return instance.time_updated.isoformat()

    def create(self, validated_data):
        '''method creating articles'''
        email = self.context.get('email')
        user = User.objects.get(email=email)
        validated_data["author"] = user

        slug = slugify(validated_data["title"])
        num = 1
        while Article.objects.filter(slug=slug).exists():
            slug = slug + "{}".format(num)
            num += 1
        validated_data["slug"] = slug
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''method updating articles'''
        email = self.context.get('email')
        if email != instance.author:
            raise PermissionDenied
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get('description', instance.description)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.time_to_read = validated_data.get('time_to_read', instance.time_to_read)
        instance.save()
        return instance
    