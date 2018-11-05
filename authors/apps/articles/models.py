<<<<<<< HEAD
'''articles/models.py'''
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

from authors.apps.authentication.models import User

class Article(models.Model):
    '''Model representing articles'''
    title = models.CharField(db_index=True, max_length=255)
    body = models.TextField()
    images = ArrayField(models.TextField(), default=None, blank=True, null=True)
    description = models.CharField(max_length=255)
    slug = models.SlugField(max_length=40, unique=True)
    tags = ArrayField(models.CharField(max_length=30), default=None, blank=True, null=True)
    time_to_read = models.IntegerField()
    # auto_now_add automatically sets the field to now when the object is first created.
    time_created = models.DateTimeField(auto_now_add=True, db_index=True)
    # auto_now will update every time you save the model.
    time_updated = models.DateTimeField(auto_now=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta():
        '''Meta class defining order'''
        ordering = ('time_created', 'time_updated',)

    def save(self, *args, **kwargs):
        '''override save from super'''
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        '''return string representation of object'''
        return self.title
=======
from django.db import models

# Create your models here.

>>>>>>> Feature(Create Articles): Add new app folder
