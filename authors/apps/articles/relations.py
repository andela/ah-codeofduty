from rest_framework import serializers

from .models import Tag

class TagRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, data):
        # if a user creates a tag that does not exist
        # we should create it

        tag, created = Tag.objects.get_or_create(tag=data)

        return tag

    def to_representation(self, value):
        '''
        returns tag property of the tag object
        '''
        return value.tag
