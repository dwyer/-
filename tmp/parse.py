#!/usr/bin/env python

import gzip
import os
import re
import sys

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'yanjiu.settings'
django.setup()

from cedict.models import Term, Translation

magic_word = 'force'

try:
    assert len(sys.argv) == 2 and sys.argv[1] == magic_word
except:
    print >>sys.stderr, 'usage: %s %s' % (os.path.basename(sys.argv[0]),
                                          magic_word)
    exit(1)

print Term.objects.all().delete()
print Translation.objects.all().delete()

regex = re.compile(r'^([^\s]*) ([^\s]*) \[(.*)\] /(.*)/$')
fp = gzip.GzipFile('data/cedict_1_0_ts_utf-8_mdbg.txt.gz')
for i, line in enumerate(fp):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if not i % 1000:
        print i
    traditional, simplified, pinyin, english = regex.match(line).groups()
    term = Term(traditional=traditional, simplified=simplified,
                  pinyin=pinyin)
    term.save()
    for translation in english.split('/'):
        translation = Translation(term=term, translation=translation)
        translation.save()
fp.close()
