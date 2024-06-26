from __future__ import unicode_literals

from django.db import models
from six import python_2_unicode_compatible
from django.contrib.auth.models import User

from polls.models import *

@python_2_unicode_compatible
class Group(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name = "members")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    open = models.IntegerField(default=0)
    def __str__(self):
        return ""