from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import User
from django.db import models

from .utils import get_terms


class Text(models.Model):

    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)
    words = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.terms.set(get_terms(self.text))
        return super(Text, self).save(*args, **kwargs)


class Phrase(models.Model):

    REVIEW_TIMES_BY_LEVEL = {
        1: datetime.timedelta(days=0),
        2: datetime.timedelta(days=1),
        3: datetime.timedelta(days=3),
        4: datetime.timedelta(days=7),
    }

    phrase = models.CharField(max_length=255, blank=False)
    translation = models.CharField(max_length=255, blank=True)
    level = models.IntegerField(null=False, default=0)
    due_date = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, null=False)

    class Meta:
        unique_together = ('phrase', 'owner')

    def __init__(self, *args, **kwargs):
        super(Phrase, self).__init__(*args, **kwargs)
        self._old_level = self.level

    def save(self, *args, **kwargs):
        self.due_date = self._calculate_due_date()
        super(Phrase, self).save(*args, **kwargs)

    def _calculate_due_date(self):
        if self.level == self._old_level:
            return self.due_date
        new_delta = self.REVIEW_TIMES_BY_LEVEL.get(self.level)
        if new_delta is None:
            return None
        old_delta = self.REVIEW_TIMES_BY_LEVEL.get(self._old_level)
        if self.due_date is not None and old_delta is not None:
            return self.due_date - old_delta + new_delta
        return datetime.datetime.now() + new_delta
