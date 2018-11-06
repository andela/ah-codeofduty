'''articles/serializers'''
from rest_framework import serializers
<<<<<<< HEAD
from django.utils.text import slugify
from authors.apps.authentication.serializers import UserSerializer
from ..authentication.models import User
from rest_framework.exceptions import PermissionDenied
<<<<<<< HEAD
# django.forms.fields.ImageField
=======
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
=======
# django.forms.fields.ImageField
>>>>>>> Feature(Create Articles): CRUD for Articles

from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
<<<<<<< HEAD
    '''Article model serializer'''
    author = UserSerializer(read_only=True)
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(max_length=1000), min_length=None, max_length=None, required=False)
=======
    author = UserSerializer(read_only=True)
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(max_length=1000), min_length=None, max_length=None, required=False)
=======
    title = serializers.CharField(required=True, max_length=100)
    body = serializers.CharField()
>>>>>>> Feature(Create Articles): CRUD for Articles
    description = serializers.CharField()
    slug = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=25), min_length=None, max_length=None, required=False)
    time_to_read = serializers.IntegerField(required=False)
    time_created = serializers.SerializerMethodField()
    time_updated = serializers.SerializerMethodField()

<<<<<<< HEAD
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
<<<<<<< HEAD
        '''method creating articles'''
=======
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
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
<<<<<<< HEAD
        '''method updating articles'''
=======
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
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
<<<<<<< HEAD
    
=======
    
>>>>>>> Feauture(Articles): Add CRUD functions for Articles
=======
    # TODO: handle images
    
    class Meta:
        model = Article
        fields = ('title', 'body', 'description', 'slug', 'tags',
                  'time_to_read', 'author', 'time_created', 'time_updated')

    def get_time_created(self, instance):
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        return instance.time_updated.isoformat()

    def create(self, validated_data):
        return Article.objects.create(**validated_data)
    
    def  update(self, instance, validated_data):
        pass
>>>>>>> Feature(Create Articles): CRUD for Articles
