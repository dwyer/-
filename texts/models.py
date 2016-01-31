from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Text(models.Model):
    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)
