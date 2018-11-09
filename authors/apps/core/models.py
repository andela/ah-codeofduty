from django.db import models


class TimeStamp(models.Model):
    """Class that sets the timestamp when the an object is created and modified"""
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
