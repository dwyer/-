from __future__ import unicode_literals

import re

from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from .. import pinyin

_chinese_regex = re.compile(r'\|?\w*[\u4e00-\u9fff]+\w*', re.UNICODE)
register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def highlight(text, term):
    if term:
        text = mark_safe(text.replace(term, '<em>%s</em>' % term))
    return text


@register.filter
@stringfilter
def pinyin_ascii_to_unicode(text):
    for match in frozenset(pinyin._REGEX.findall(text)):
        try:
            text = text.replace(match, pinyin.ascii_to_unicode(match))
        except ValueError:
            pass
    return text


@register.filter(is_safe=True)
@stringfilter
def urlize_chinese(text):
    for phrase in frozenset(_chinese_regex.findall(text)):
        if phrase.startswith('|'):
            continue
        text = text.replace(phrase, '<a href="%s">%s</a>' % (
            '#', # TODO make this a valid URL
            phrase,
        ))
    return mark_safe(text)
