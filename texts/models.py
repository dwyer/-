from __future__ import unicode_literals

import datetime
import random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .utils import get_terms


class GetOrInstatiateMixin(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def get_or_instantiate(cls, defaults=None, **kwargs):
        try:
            obj = cls.objects.get(**kwargs)
            created = False
        except cls.DoesNotExist:
            if defaults is not None:
                kwargs.update(defaults)
            obj = cls(**kwargs)
            created = True
        return (obj, created)


class Text(models.Model):

    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)
    words = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.words = '\n'.join(get_terms(self.text))
        return super(Text, self).save(*args, **kwargs)

    def phrases(self, user):
        phrases = []
        for word in self.words.splitlines():
            phrases.append(
                Phrase.get_or_instantiate(phrase=word, owner=user)[0])
        return phrases


class Phrase(GetOrInstatiateMixin, models.Model):

    REVIEW_TIMES_BY_LEVEL = {
        1: 0,
        2: 1,
        3: 3,
        4: 7,
        5: 15,
    }

    phrase = models.CharField(max_length=255, blank=False)
    translation = models.CharField(max_length=255, blank=True)
    romanization = models.CharField(max_length=255, blank=True)
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
        if True:
            days = self.REVIEW_TIMES_BY_LEVEL.get(self.level)
            if days is not None:
                rand = 1 - 0.2 * random.random()
                delta = timezone.timedelta(days=days*rand)
                print self.level, days, delta
                self.due_date = timezone.now() + delta
            else:
                self.due_date = None
        super(Phrase, self).save(*args, **kwargs)


class PhraseTag(models.Model):

    name = models.CharField(max_length=255, blank=False, unique=True)
    phrases = models.ManyToManyField(Phrase)

    def __str__(self):
        return self.name
