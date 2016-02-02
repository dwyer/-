from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from .utils import get_sentences


class Text(models.Model):
    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)

    @property
    def processed_text(self):
        return ''.join(get_sentences(self.text))
