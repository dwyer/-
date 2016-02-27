from __future__ import unicode_literals

import re

from django.core.cache import cache

from cedict.models import Term

_ZH_SENT_REGEX = re.compile(r'[\u4e00-\u9fa5]+')


def process_text(text):
    terms = {}
    for term in (text.terms.extra(select={'L': 'Length(traditional)'})
                 .order_by('-L')):
        if term.traditional[0] not in terms:
            terms[term.traditional[0]] = []
        terms[term.traditional[0]].append(term.traditional)
    text = text.text
    fragments = []
    while text:
        term = None
        for term in terms.get(text[0], []):
            if text.startswith(term):
                break
        if term is None:
            fragments.append(text[0])
            text = text[1:]
        else:
            fragments.append('<span class="zh-word">%s</span>' % term)
            text = text[len(term):]
    return ''.join(fragments)


def get_terms(text):
    key_prefix = 'get_terms:term:'
    text = text.text
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
