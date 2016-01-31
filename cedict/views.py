from __future__ import unicode_literals

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from cedict.models import Phrase

MAX_RESULTS = 20


def index(request):
    return render(request, 'base.html', {})


def phrase_list(request):
    search_query = request.GET.get('q', '')
    page_number = int(request.GET.get('p', '1'))
    terms = set(search_query.split())
    if 'is:starred' in terms:
        terms.remove('is:starred')
        phrases = request.user.profile.starred_phrases.order_by('traditional')
    else:
        phrases = (Phrase.objects
                   .extra(select={'__len': 'Length(traditional)'})
                   .order_by('__len'))
    for term in terms:
        phrases = phrases.filter(Q(traditional__contains=term)
                                 |Q(simplified__contains=term))
    paginator = Paginator(phrases, MAX_RESULTS)
    page = paginator.page(page_number)
    phrases = page.object_list
    context = {
        'page': page,
        'phrases': phrases,
        'search_query': search_query,
    }
    return render(request, 'phrase_list.html', context)


def phrase_view(request, traditional=None, simplified=None):
    if traditional:
        phrases = Phrase.objects.filter(traditional=traditional)
    elif simplified:
        phrases = Phrase.objects.filter(simplified=simplified)
    else:
        pass # TODO raise 400 error
    if not phrases.count():
        raise Http404
    context = {
        'phrases': phrases,
    }
    return render(request, 'phrase_list.html', context)


def random_phrase(request):
    phrase = Phrase.objects.order_by('?').first().traditional
    return HttpResponseRedirect(reverse('cedict_phrase_tw', args=(phrase,)))
