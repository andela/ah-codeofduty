from django.db import models

from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStamp


class UserProfile(TimeStamp):
    """Class description of user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
