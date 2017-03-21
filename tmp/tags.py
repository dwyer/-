#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import random

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from texts.models import Phrase, PhraseTag

from django.db.models import Avg


phrase = Phrase.objects.order_by('?').first()
print phrase.phrase
print phrase.phrasetag_set.all()

tag = PhraseTag(name='number')
tag.save()
