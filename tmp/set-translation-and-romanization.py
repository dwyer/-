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

num_saved = 0
num_total = 0
for phrase in Phrase.objects.all():
    if phrase.translation and phrase.romanization:
        continue
    num_total += 1
    print phrase.phrase, phrase.translation, phrase.romanization
    terms = Term.objects.filter(traditional=phrase.phrase)
    lst = []
    for term in terms:
        for translation in term.translation_set.all():
            lst.append((term.pinyin, translation.translation))
    for i, (romanization, translation) in enumerate(lst):
        print '    %d /%s/ %s' % (i+1, romanization, translation)
    if len(lst) == 0:
        translation = raw_input('translation> ')
        romanization = raw_input('romanization> ')
        if translation:
            phrase.translation = translation
        if romanization:
            phrase.romanization = romanization
        if translation or romanization:
            phrase.save()
            num_saved += 1
    elif len(lst) == 1:
        romanization, translation = lst[0]
        phrase.translation = translation
        phrase.romanization = romanization
        phrase.save()
        num_saved += 1
    else:
        try:
            n = int(raw_input('# ')) - 1
        except ValueError:
            continue
        if n < 0 or n >= len(lst):
            n = None
        else:
            romanization, translation = lst[0]
            phrase.translation = translation
            phrase.romanization = romanization
            phrase.save()
            num_saved += 1

print 'saved %d/%d' % (num_saved, num_total)
