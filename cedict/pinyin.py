# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import sys

_SPECIAL_FINALS = ('a', 'e', 'ou')
_REGEX = re.compile(r'([A-Za-z]+)([1-5])')
_MAP = {
    u'a': (u'ā', u'á', u'ǎ', u'à'),
    u'e': (u'ē', u'é', u'ě', u'è'),
    u'i': (u'ī', u'í', u'ǐ', u'ì'),
    u'o': (u'ō', u'ó', u'ǒ', u'ò'),
    u'u': (u'ū', u'ú', u'ǔ', u'ù'),
    u'ü': (u'ǖ', u'ǘ', u'ǚ', u'ǜ'),
}


def _accent(alpha, tone, index=None):
    if tone == 5:
        return alpha
    if index is not None:
        return alpha[:index] + _MAP[alpha[index]][tone-1] + alpha[index+1:]
    alpha = alpha.replace('v', u'ü')
    for c in _SPECIAL_FINALS:
        try:
            index = alpha.index(c)
        except ValueError:
            pass
        else:
            return _accent(alpha, tone, index)
    for i in xrange(len(alpha)-1, -1, -1):
        if alpha[i] in _MAP:
            return _accent(alpha, tone, i)
    raise ValueError


def ascii_to_unicode(phrase):
    components = []
    for syllable in phrase.split():
        match = _REGEX.match(syllable)
        if match is None:
            raise ValueError('Not a pinyin syllable: %r' % syllable)
        components.append(_accent(match.group(1), int(match.group(2))))
    return ' '.join(components)
