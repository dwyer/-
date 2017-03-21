#!/usr/bin/env python
from __future__ import unicode_literals

import os
import sys

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from texts.models import Text

if len(sys.argv) == 2:
    query = sys.argv[1].decode('utf-8')
else:
    print >>sys.stderr, 'usage: %s SEARCH_QUERY' % os.path.basename(sys.argv[0])
    exit(1)

boldquery = '\033[1m%s\033[0m' % query
queryset = Text.objects.order_by('title')
for text in Text.objects.filter(text__icontains=query):
    for lineno, line in enumerate(text.text.splitlines()):
        if query in line:
            line = line.replace(query, boldquery)
            print '%s: line %d: %s' % (text.title, lineno + 1, line)
