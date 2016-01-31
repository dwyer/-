from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Phrase(models.Model):
    traditional = models.CharField(max_length=255, blank=False)
    simplified = models.CharField(max_length=255, blank=False)
    pinyin = models.CharField(max_length=255, blank=False)


class Translation(models.Model):
    phrase = models.ForeignKey(Phrase, null=False)
    translation = models.TextField(blank=False)


class Profile(models.Model):
    user = models.OneToOneField(User)
    starred_phrases = models.ManyToManyField(Phrase)


class Text(models.Model):
    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(User, null=False)


@receiver(post_save, sender=User, dispatch_uid='user_post_save')
def user_post_save(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
