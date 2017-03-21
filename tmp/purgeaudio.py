#!/usr/bin/env python

import datetime
import os

MAX_AGE = 30

dirname = '.tmp/media/audio_files'
now = datetime.datetime.now()

for filename in os.listdir(dirname):
    path = os.path.join(dirname, filename)
    accessed = datetime.datetime.fromtimestamp(os.path.getatime(path))
    age = (now - accessed).days
    if age > MAX_AGE:
        print 'removing %d day old %s' % (age, path)
        os.remove(path)
