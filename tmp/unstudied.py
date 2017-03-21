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

for i, phrase in enumerate(Phrase.objects.filter(level=0)):
    print '%d. %s /%s/ %s' % (i+1, phrase.phrase, phrase.romanization,
                              phrase.translation)
