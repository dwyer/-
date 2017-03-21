#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import random

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from cedict.models import Term
from texts.models import Phrase, Text

chars_old = set()
chars_new = set()
words = set()
phrases = Phrase.objects.all()
for phrase in phrases:
    word = phrase.phrase
    if len(word) == 1:
        words.add(word)
    else:
        for char in word:
            if phrase.level == 5:
                chars_old.add(char)
            else:
                chars_new.add(char)

chars_new = chars_new - chars_old

print ' '.join(sorted(chars_old - words)).encode('utf-8')
print
print ' '.join(sorted(chars_new - words)).encode('utf-8')
