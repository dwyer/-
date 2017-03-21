#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import re
import sqlite3
import time

import django
from django.db.models.query_utils import Q

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from cedict.models import Term

regex = re.compile(r'^(\S+) (\d+\.\d+) ([01]) ([a-z\s]+)$')

lst = []

# connection = sqlite3.connect('db.sqlite3')
# cursor = connection.cursor()
re2 = re.compile(r'\d')


for term in Term.objects.filter(frequency__gt=0).order_by('-frequency')[:100]:
    print term.traditional.encode('utf-8')
exit()


terms = Term.objects.filter(frequency__gt=0).order_by('-frequency')[:200]
for term in terms:
    print term.frequency, term.traditional
print terms.count()
exit()

with open('rawdict_utf16_65105_freq.txt', 'rb') as fp:
    text = fp.read()

assert text.startswith(codecs.BOM_UTF16_LE)
text = text[len(codecs.BOM_UTF16_LE):]
text = text.decode('utf-16le')
text = text.encode('utf-8')
lines = text.splitlines()

start = time.time()
for i, line in enumerate(lines):
    if not i % 1000:
        print i, len(lines), time.time() - start
    # print line
    word, freq, trad, pinyin = regex.match(line).groups()
    freq = float(freq)
    trad = bool(int(trad))
    if 'nv' in pinyin:
        pinyin = re.sub(r'nv', 'nu:', pinyin)
        terms = Term.objects.filter(Q(traditional=word)|Q(simplified=word))
        for term in terms:
            if pinyin == re2.sub('', term.pinyin):
                term.frequency += freq
                term.save()
    continue
    terms = Term.objects.filter(Q(traditional=word)|Q(simplified=word))
    for term in terms:
        # print term.pinyin, re2.sub('', term.pinyin)
        if pinyin == re2.sub('', term.pinyin):
            term.frequency += freq
            term.save()
            # print pinyin, word, term.traditional, term.simplified, term.pinyin
