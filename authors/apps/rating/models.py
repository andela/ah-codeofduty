"""
Ratings Model module
"""

from django.db import models

from authors.apps.articles.models import Article
from authors.apps.authentication.models import User

# Create your models here.


class Rating(models.Model):
    """
    Rating class model
    :param: models.Model: parent class parameter
    """
    rating = models.IntegerField(null=False, default=0)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    rater = models.ForeignKey(User, on_delete=models.CASCADE)

    def __int__(self):
        """
        special method to return data in human
        readable form
        """
        return self.rating
