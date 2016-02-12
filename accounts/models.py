from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from cedict.models import Phrase


class Profile(models.Model):
    user = models.OneToOneField(User)
    starred_phrases = models.ManyToManyField(Phrase)


@receiver(post_save, sender=User, dispatch_uid='user_post_save')
def user_post_save(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
