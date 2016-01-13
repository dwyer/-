import subprocess
import tempfile

from django.core.files.storage import get_storage_class
from django.http import HttpResponseRedirect

_storage = get_storage_class()()


def audio_view(request, phrase):
    phrase = phrase.replace('u:', 'v')
    phrase = ' '.join('er' if comp == 'r' else comp for comp in phrase.split())
    filename = 'audio_files/%s.mp4' % phrase
    if not _storage.exists(filename):
        with tempfile.NamedTemporaryFile(suffix='.mp4') as audio_file:
            subprocess.call(('say', '--file-format=mp4f', '-o',
                             audio_file.name, '-v', 'Mei-Jia', phrase))
            with _storage.open(filename, 'wb') as dest:
                dest.write(audio_file.read())
    return HttpResponseRedirect(_storage.url(filename))
