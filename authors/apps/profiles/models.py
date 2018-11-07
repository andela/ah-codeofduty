from django.db import models

from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStamp


class Profile(TimeStamp):
    """Class description of user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField('self',
                                     related_name='followed_by',
                                     symmetrical=False)
    favorites = models.ManyToManyField('articles.Article',
                                       related_name='favorited_by')
    surname = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        """ Follow profile """
        self.follows.add(profile)

    def unfollow(self, profile):
        """ Unfollow profile """
        self.follows.remove(profile)

    def is_following(self, profile):
        """ Returns True if following profile; else False """
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, profile):
        """ Returns True if being followed by profile; else False """
        return self.follows.filter(pk=profile.pk).exists()

    def get_followers(self, profile):
        """ Get profile followers """
        return profile.followed_by.all()

    def get_following(self, profile):
        """ Get profiles user is following """
        return profile.follows.all()

    def favorite(self, article):
        self.favorites.add(article)
    
    def unfavorite(self, article):
        self.favorites.remove(article)
    
    def favorited(self, article):
        return self.favorites.filter(pk=article.pk).exists()
