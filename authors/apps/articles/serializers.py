'''articles/serializers'''
import math
from decimal import Decimal
from django.db.models import Avg
from rest_framework import serializers
from django.utils.text import slugify
from authors.apps.authentication.serializers import UserSerializer
from ..authentication.models import User
from rest_framework.exceptions import PermissionDenied
from authors.apps.authentication.models import User
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile

from .models import Article, Comment, CommentHistory, Highlight
from ..rating.models import Rating


class ArticleSerializer(serializers.ModelSerializer):
    '''Article model serializer'''
    author = UserSerializer(read_only=True)
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(
        max_length=1000), min_length=None, max_length=None, required=False)
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
    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField(
        method_name='get_favorites_count')
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('title', 'body', 'images', 'description', 'slug', 'tags',
                  'time_to_read', 'author', 'time_created', 'time_updated',
                  'favorited', 'favoritesCount', 'average_rating')

    def get_time_created(self, instance):
        '''get time the article was created and return in iso format'''
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        '''get time the article was updated and return in iso format'''
        return instance.time_updated.isoformat()

    def get_time_to_read(self, text, images):
        '''method calculating time it takes to read'''
        # time to read is calculated using words per minute
        # the reading speed of an average person is about 150-250 wpm
        # it takes 12 seconds to view an inline image
        average_image_view_time = 0
        if images:
            average_image_view_time = (len(images) * 0.2)
        return math.ceil(((len(text.split()) / 200) + average_image_view_time))

    def create(self, validated_data):
        '''method creating articles'''
        email = self.context.get('email')
        user = User.objects.get(email=email)
        validated_data["author"] = user
        images = validated_data.get("images", None)

        slug = slugify(validated_data["title"])
        num = 1
        while Article.objects.filter(slug=slug).exists():
            slug = slug + "{}".format(num)
            num += 1
        validated_data["slug"] = slug
        validated_data["time_to_read"] = self.get_time_to_read(
            validated_data["body"], images)

        return Article.objects.create(**validated_data)

    def get_average_rating(self, obj):
        avarage = 0
        try:
            ratings = Rating.objects.filter(article=obj.id)
            avarage = ratings.all().aggregate(
                Avg('rating'))['rating__avg']
        except Exception as e:
            print(e)
        return avarage

    def update(self, instance, validated_data):
        '''method updating articles'''
        email = self.context.get('email')
        if email != instance.author:
            raise PermissionDenied
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.images = validated_data.get('images', instance.images)
        instance.time_to_read = self.get_time_to_read(instance.body, instance.images)
        instance.save()
        return instance

    def get_favorited(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.profile.has_favorited(instance)

    def get_favorites_count(self, instance):
        return instance.favorited_by.count()


class RecursiveSerializer(serializers.Serializer):
    """
    This class deals with a comment within a comment
    """

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """
    This class creates the comments serializers
    """
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

    def update(self, instance, valid_input, **kwargs):
        """
        Update and return a comment instance, given valid_input
        """
        instance.body = valid_input.get('body', instance.body)
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

    def create(self, valid_input):
        """
        Create and return a new comment instance, given a valid_input
        """
        parent = self.context.get('parent', None)
        instance = Comment.objects.create(parent=parent, **valid_input)
        return instance

class CommentHistorySerializer(serializers.ModelSerializer):
    """comment history serializer"""
    class Meta:
        model = CommentHistory
        fields = ('id', 'comment', 'date_created', 'parent_comment')

class HighlightSerializer(serializers.ModelSerializer):
    '''Highlight model serializer'''
    article = ArticleSerializer(read_only=True)
    highlighter = UserSerializer(read_only=True)
    index_start = serializers.IntegerField()
    index_stop = serializers.IntegerField()
    highlighted_article_piece = serializers.CharField(
        required=False, max_length=200)
    comment = serializers.CharField(required=False, max_length=200)

    class Meta:
        model = Highlight
        fields = ('article', 'highlighter', 'index_start',
                  'index_stop', 'highlighted_article_piece', 'comment')

    def create(self, validated_data):
        '''method creating a new highlight'''
        validated_data["highlighter"] = self.context.get('highlighter')
        validated_data["article"] = self.context.get('article')
        highlight_text = validated_data["article"].body[
            validated_data["index_start"]:validated_data["index_stop"]]
        if not highlight_text:
            raise serializers.ValidationError("Text doesn't exist on this article")
        validated_data["highlighted_article_piece"] = highlight_text

        return Highlight.objects.create(**validated_data)

    def update(self, instance, validated_data):
        '''method updating highlights'''
        user = self.context.get('user')
        if user != instance.highlighter:
            raise PermissionDenied
        index_start = validated_data.get('index_start', instance.index_start)
        index_stop = validated_data.get('index_stop', instance.index_stop)
        highlight_text = instance.article.body[index_start:index_stop]
        if not highlight_text:
            raise serializers.ValidationError("Text doesn't exist on this article")
        instance.comment = validated_data.get('comment', instance.comment)
        instance.index_start = index_start
        instance.index_stop = index_stop
        instance.highlighted_article_piece = highlight_text
        instance.save()
        return instance
