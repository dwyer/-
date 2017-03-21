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

phrases = Phrase.objects.filter(level=5)
for i, phrase in enumerate(phrases):
    print i, phrase.phrase, phrase.updated, phrase.due_date
