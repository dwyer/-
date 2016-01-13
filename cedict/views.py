from __future__ import unicode_literals

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from cedict.models import Phrase


def index_view(request):
    phrases = Phrase.objects.all()[:100]
    context = {'phrases': phrases}
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


def search_view(request):
    search_query = request.GET.get('q', '')
    phrases = (Phrase.objects.filter(Q(traditional__contains=search_query)
                                     |Q(simplified__contains=search_query))
               .extra(select={'__len': 'Length(traditional)'})
               .order_by('__len'))
    context = {'phrases': phrases, 'search_query': search_query}
    return render(request, 'phrase_list.html', context)
