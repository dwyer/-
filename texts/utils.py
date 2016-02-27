from __future__ import unicode_literals

import re

from django.core.cache import cache

from cedict.models import Term

_ZH_SENT_REGEX = re.compile(r'[\u4e00-\u9fa5]+')


def process_text(text):
    key_prefix = 'get_words:term:'
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
        offset = index + len(sentence)
        while sentence:
            done = False
            first = sentence[0]
            terms = cache.get(key_prefix + first)
            if terms is None:
                terms = (Term.objects
                         .filter(traditional__startswith=first)
                         .extra(select={'L': 'Length(traditional)'})
                         .order_by('-L')
                         .values('traditional'))
                cache.set(key_prefix + first, terms)
            for term in terms:
                term = term['traditional']
                if sentence.startswith(term):
                    sentence = sentence[len(term):]
                    done = True
                    fragments.append('<span class="zh-word">%s</span>' % term)
                    break
            if done:
                continue
            fragments.append(first)
            sentence = sentence[1:]
        text = text[offset:]
    return ''.join(fragments)
