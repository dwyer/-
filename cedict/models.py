from __future__ import unicode_literals

from django.db import models

from . import pinyin


class Phrase(models.Model):
    traditional = models.CharField(max_length=255, blank=False)
    simplified = models.CharField(max_length=255, blank=False)
    pinyin = models.CharField(max_length=255, blank=False)

    @property
    def pinyin_unicode(self):
        return pinyin.ascii_to_unicode(self.pinyin)

    @property
    def zhuyin(self):
        return pinyin.zhuyin(self.pinyin)


class Translation(models.Model):
    phrase = models.ForeignKey(Phrase, null=False)
    translation = models.TextField(blank=False)
