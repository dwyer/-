#!/usr/bin/env python

import gzip
import os
import re

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from cedict.models import Phrase, Translation

for i, phrase in enumerate(Phrase.objects.all()):
    pinyin = ' '.join('er5' if comp == 'r1' else comp
                      for comp in phrase.pinyin.split())
    if phrase.pinyin != pinyin:
        print i, phrase.pinyin
        phrase.pinyin = pinyin
        phrase.save()
