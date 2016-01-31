from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from cedict.models import Phrase


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
