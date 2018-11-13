"""articles/models.py"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
from authors.apps.authentication.models import User


class Article(models.Model):
    """Model representing articles"""
    title = models.CharField(db_index=True, max_length=255)
    body = models.TextField()
    images = ArrayField(models.TextField(), default=None,
                        blank=True, null=True)
    description = models.CharField(max_length=255)
    slug = models.SlugField(max_length=40, unique=True)
    tags = ArrayField(models.CharField(max_length=30),
                      default=None, blank=True, null=True)
    time_to_read = models.IntegerField()
    # auto_now_add automatically sets the field to now when the object is first created.
    time_created = models.DateTimeField(auto_now_add=True, db_index=True)
    # auto_now will update every time you save the model.
    time_updated = models.DateTimeField(auto_now=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    average_rating = models.IntegerField(default=0)

    class Meta():
        """Meta class defining order"""
        ordering = ('time_created', 'time_updated',)

    def save(self, *args, **kwargs):
        """override save from super"""
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of object"""
        return self.title


class Comment(models.Model):
    """
    This class implement a database table.
    This table has  seven fields one is automatically generated by django
    The relationship between articles and comments is one to many
    The relationship between comment and reply is one to many.
    the relationship between Author and comments is one to many
    """
    parent = models.ForeignKey(
        'self', null=True, blank=False, on_delete=models.CASCADE, related_name='thread')
    article = models.ForeignKey(
        Article, blank=True, null=True, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    def __str__(self):
        return self.body


class CommentHistory(models.Model):
    """
     implements comment edit history table
    """
    comment = models.TextField()
    parent_comment = models.ForeignKey(Comment,
                                       on_delete=models.CASCADE,
                                       db_column='parent_comment')
    date_created = models.DateTimeField(auto_now=True)


class Highlight(models.Model):
    """
    Table representing highlights and comments made on articles
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name="highlights")
    highlighter = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name="highlights")
    index_start = models.IntegerField(default=0)
    index_stop = models.IntegerField()
    highlighted_article_piece = models.CharField(blank=True, max_length=200)
    comment = models.CharField(blank=True, max_length=200)
    time_created = models.DateTimeField(auto_now_add=True, db_index=True)
    time_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta():
        '''Meta class defining order'''
        ordering = ('time_updated',)

    def __str__(self):
        return self.comment
class Report(models.Model):
    """Reporting an article model"""
    body = models.TextField()
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body
