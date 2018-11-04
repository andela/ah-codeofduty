'''articles/serializers'''
from rest_framework import serializers
from django.utils.text import slugify
from authors.apps.authentication.serializers import UserSerializer
from ..authentication.models import User
from rest_framework.exceptions import PermissionDenied

from .models import Article
from .models import Comment
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.authentication.models import User


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(
        max_length=1000), min_length=None, max_length=None, required=False)
    description = serializers.CharField()
    slug = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(
        max_length=25), min_length=None, max_length=None, required=False)
    time_to_read = serializers.IntegerField(required=False)
    time_created = serializers.SerializerMethodField()
    time_updated = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('title', 'body', 'images', 'description', 'slug', 'tags',
                  'time_to_read', 'author', 'time_created', 'time_updated')

    def get_time_created(self, instance):
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        return instance.time_updated.isoformat()

    def create(self, validated_data):
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
        email = self.context.get('email')
        if email != instance.author:
            raise PermissionDenied
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.time_to_read = validated_data.get(
            'time_to_read', instance.time_to_read)
        instance.save()
        return instance


# ............................................................................................
class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """This class creates the comments serializers"""

    author = serializers.SerializerMethodField()
    article = serializers.ReadOnlyField(source='article.title')
    thread = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Comment

        fields = (
            'id',
            'body',
            'article',
            'author',
            'thread',
            'created_at',
            'updated_at'
        )

    def update(self, instance, validated_data, **kwargs):
        """
        Update and return a comment instance, given the validated_data
        """
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance

    def get_author(self, obj):
        try:
            author = obj.author
            profile = Profile.objects.get(user_id=author.id)
            serializer = ProfileSerializer(profile)
            return serializer.data
        except Exception as e:
            return {}

    def create(self, validated_data):
        """
        Create and return a new comment instance, given the validated_data
        """
        parent = self.context.get('parent', None)
        instance = Comment.objects.create(parent=parent, **validated_data)
        return instance
