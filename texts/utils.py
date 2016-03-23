from __future__ import unicode_literals

import re

from django.core.cache import cache

from cedict.models import Term

_ZH_SENT_REGEX = re.compile(r'[\u4e00-\u9fa5]+')


def get_terms(text):
    key_prefix = 'get_terms:term:'
    fragments = set()
    while text:
        match = _ZH_SENT_REGEX.search(text)
        if not match:
            break
        sentence = match.group(0)
        index = text.index(sentence)
        offset = index + len(sentence)
        while sentence:
            done = False
            first = sentence[0]
            terms = cache.get(key_prefix + first)
            if terms is None:
                terms = (Term.objects
                         .filter(traditional__startswith=first)
                         .extra(select={'L': 'Length(traditional)'})
                         .order_by('-L'))
                cache.set(key_prefix + first, terms)
            for term in terms:
                if sentence.startswith(term.traditional):
                    sentence = sentence[len(term.traditional):]
                    done = True
                    fragments.add(term)
                    break
            if done:
                continue
            sentence = sentence[1:]
        text = text[offset:]
    return fragments
