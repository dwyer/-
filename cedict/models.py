from __future__ import unicode_literals

from django.db import models

from . import pinyin


class Term(models.Model):
    traditional = models.CharField(max_length=255, blank=False)
    simplified = models.CharField(max_length=255, blank=False)
    pinyin = models.CharField(max_length=255, blank=False)
    frequency = models.FloatField(default=0)

    @property
    def pinyin_unicode(self):
        return pinyin.ascii_to_unicode(self.pinyin)

    @property
    def zhuyin(self):
        return pinyin.zhuyin(self.pinyin)


class Translation(models.Model):
    term = models.ForeignKey(Term, null=False)
    translation = models.TextField(blank=False)
