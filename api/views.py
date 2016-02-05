from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework import generics, pagination, viewsets

from cedict.models import Phrase, Translation
from texts.models import Text

from . import serializers
from . import permissions


class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = serializers.PhraseSerializer
    permission_classes = (permissions.ReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        traditional = self.request.query_params.get('traditional')
        search_query = self.request.query_params.get('q')
        if search_query is not None:
            queryset = (queryset.filter(traditional__contains=search_query)
                        .extra(select={'__len': 'Length(traditional)'})
                        .order_by('__len'))
        if traditional is not None:
            queryset = queryset.filter(traditional=traditional)
        return queryset


class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = serializers.TranslationSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)


class TextViewSet(viewsets.ModelViewSet):
    queryset = Text.objects.all()
    serializer_class = serializers.TextSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)


class PhrasesStar(View):

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
