from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from cedict.models import Phrase, Text
from cedict.forms import TextForm

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


class TextList(View):

    def get(self, request):
        texts = Text.objects.all()
        # TODO: paginate
        context = {
            'texts': texts,
        }
        return render(request, 'text_list.html', context)


class TextDetail(View):

    def get(self, request, pk):
        text = get_object_or_404(Text, pk=pk)
        context = {'text': text}
        return render(request, 'text_detail.html', context)


class TextEdit(View):

    def get_text(self, request, pk):
        if pk is None:
            return None
        text = get_object_or_404(Text, pk=pk)
        if text.owner != request.user:
            raise PermissionDenied
        return text

    def get(self, request, pk=None):
        text = self.get_text(request, pk)
        form = TextForm(instance=text)
        return render(request, 'text_edit.html', {'form': form})

    def post(self, request, pk=None):
        text = self.get_text(request, pk)
        form = TextForm(request.POST, instance=text)
        if not form.is_valid():
            return render(request, 'text_edit.html', {'form': form})
        text = form.save(commit=False)
        text.owner = request.user
        text.save()
        return HttpResponseRedirect(reverse('text_detail', args=(text.pk,)))


class ApiPhrase(View):

    def get(self, request, phrase):
        lst = []
        for phrase in Phrase.objects.filter(traditional=phrase):
            obj = {
                'traditional': phrase.traditional,
                'simplified': phrase.simplified,
                'pinyin': phrase.pinyin,
                'translations': [],
            }
            for translation in phrase.translation_set.all():
                obj['translations'].append(translation.translation)
            lst.append(obj)
        return JsonResponse({'phrases': lst})


class ApiPhrasesStar(View):

    # TODO: require login
    def post(self, request, phrase_id):
        phrase = get_object_or_404(Phrase, pk=phrase_id)
        request.user.profile.starred_phrases.add(phrase)
        return JsonResponse({})

    # TODO: require login
    def delete(self, request, phrase_id):
        phrase = get_object_or_404(Phrase, pk=phrase_id)
        request.user.profile.starred_phrases.remove(phrase)
        return JsonResponse({})
