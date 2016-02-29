from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.html import strip_tags

from cedict.models import Term

from .utils import get_terms, process_text


class Text(models.Model):
    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)
    terms = models.ManyToManyField(Term)

    @property
    def processed_text(self):
        return process_text(self)

    def save(self, *args, **kwargs):
        self.text = strip_tags(self.text)
        self.terms.set(get_terms(self))
        return super(Text, self).save(*args, **kwargs)


class Phrase(models.Model):
    phrase = models.CharField(max_length=255, blank=False)
    owner = models.ForeignKey(User, null=False)
    level = models.IntegerField(null=False, default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('phrase', 'owner')
