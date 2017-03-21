#!/usr/bin/env python
from __future__ import unicode_literals

import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from texts.models import Phrase

from django.db.models import Avg
from django.utils import timezone

user = 1

q = Phrase.objects.filter(owner=user)
due_count = q.filter(due_date__lt=timezone.now()).count()
words_saved = q.count()

q = q.filter(level__gt=0)

word_count = q.count()
word_score = q.aggregate(Avg('level'))['level__avg']
words_mastered = q.filter(level=5).count()

char_total = len(reduce(set.union, (set(p.phrase) for p in q)))

q = q.extra(where=['length(phrase) = 1'])
char_count = q.count()
char_score = q.aggregate(Avg('level'))['level__avg']
chars_mastered = q.filter(level=5).count()

print '%d/%d words studied' % (word_count, words_saved)
print '%d/%d (%d%%) words mastered' % (words_mastered,
                                       word_count,
                                       100 * words_mastered / word_count)
print 'word score: %g' % word_score
print '%d/%d (%d%%) chars studied' % (char_count,
                                      char_total,
                                      100 * char_count / char_total)
print '%d/%d (%d%%) chars mastered' % (chars_mastered,
                                       char_count,
                                       100 * chars_mastered / char_count)
print 'char score: %g' % char_score
print '%d flashcards due' % due_count
