from __future__ import unicode_literals

from django.db import models


class Phrase(models.Model):
    traditional = models.CharField(max_length=255, blank=False)
    simplified = models.CharField(max_length=255, blank=False)
    pinyin = models.CharField(max_length=255, blank=False)


class Translation(models.Model):
    phrase = models.ForeignKey(Phrase, null=False)
    translation = models.TextField(blank=False)
