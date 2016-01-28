from __future__ import unicode_literals

import re
import sys

_REGEX = re.compile(r'[A-Za-z:]+[1-5]')
_MAP = {
    'a': ('\u0101', '\xe1', '\u01ce', '\xe0'),
    'e': ('\u0113', '\xe9', '\u011b', '\xe8'),
    'i': ('\u012b', '\xed', '\u01d0', '\xec'),
    'o': ('\u014d', '\xf3', '\u01d2', '\xf2'),
    'u': ('\u016b', '\xfa', '\u01d4', '\xf9'),
    '\xfc': ('\u01d6', '\u01d8', '\u01da', '\u01dc'),
}


# TODO: cache
def _accent(alpha, tone, index=None):
    if tone == 5:
        return alpha
    if index is not None:
        return alpha[:index] + _MAP[alpha[index]][tone-1] + alpha[index+1:]
    alpha = alpha.replace('u:', 'v')
    alpha = alpha.replace('v', '\xfc')
    for c in ('a', 'e', 'ou'):
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


# TODO: cache
def ascii_to_unicode(phrase):
    components = []
    for syllable in phrase.split():
        match = _REGEX.match(syllable)
        if match is None:
            raise ValueError('Not a pinyin syllable: %r' % syllable)
        match = match.group(0)
        components.append(_accent(match[:-1], int(match[-1])))
    return ' '.join(components)
