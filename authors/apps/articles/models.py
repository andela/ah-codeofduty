'''articles/models.py'''
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

from authors.apps.authentication.models import User

class Article(models.Model):
    title = models.CharField(db_index=True, max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', null=True, blank=True, height_field=100, width_field=100, max_length=100)
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
        ordering = ('time_created', 'time_updated',)

    def create_slug(self):
        '''create a unique slug from title'''
        slug = slugify(self.title)
        num = 1
        while Article.objects.filter(slug=slug).exists():
            slug = slug + "{}".format(num)
            num += 1
        return slug

    def get_time_created(self, instance):
        return instance.time_created.isoformat()

    def get_time_updated(self, instance):
        return instance.time_updated.isoformat()

    def save(self, *args, **kwargs):
        '''override save from super'''
        self.slug = self.create_slug()
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
