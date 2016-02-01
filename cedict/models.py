from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class Profile(models.Model):
    user = models.OneToOneField(User)
    starred_phrases = models.ManyToManyField(Phrase)


@receiver(post_save, sender=User, dispatch_uid='user_post_save')
def user_post_save(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
