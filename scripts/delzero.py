#!/usr/bin/env python
from __future__ import unicode_literals

import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from texts.models import Phrase

q = Phrase.objects.filter(level=0)
for phrase in q:
    print phrase.phrase
    phrase.delete()
print q.count()
