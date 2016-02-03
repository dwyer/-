from __future__ import unicode_literals

import re

from django.core.cache import cache

from cedict.models import Phrase

_ZH_SENT_REGEX = re.compile(r'[\u4e00-\u9fa5]+')
_CACHE_PREFIX = 'get_words:phrase:'


def _get_words(sentence):
    words = []
    while sentence:
        done = False
        key = sentence[0]
        phrases = cache.get(_CACHE_PREFIX + key)
        if phrases is None:
            phrases = (Phrase.objects
                          .filter(traditional__startswith=key)
                          .extra(select={'L': 'Length(traditional)'})
                          .order_by('-L')
                          .values('traditional'))
            cache.set(_CACHE_PREFIX + key, phrases)
        for phrase in phrases:
            phrase = phrase['traditional']
            if sentence.startswith(phrase):
                sentence = sentence[len(phrase):]
                done = True
                words.append('<span class="zh-word">%s</span>' % phrase)
                break
        if done:
            continue
        words.append(key)
        sentence = sentence[1:]
    return words


def _get_sentences(text):
    fragments = []
    while text:
        match = _ZH_SENT_REGEX.search(text)
        if not match:
            fragments.append(text)
            break
        sentence = match.group(0)
        index = text.index(sentence)
        if index:
            fragments.append(text[:index])
        fragments.append('<span class="zh-sent">')
        fragments.extend(_get_words(sentence))
        fragments.append('</span>')
        text = text[index + len(sentence):]
    return fragments


def process_text(text):
    return ''.join(_get_sentences(text))
