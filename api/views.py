import subprocess
import tempfile

from django.contrib.auth.models import User
from django.core.files.storage import get_storage_class
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework import generics, pagination, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from cedict.models import Term, Translation
from texts.models import Text

from . import serializers
from . import permissions

_storage = get_storage_class()()


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = serializers.TermSerializer
    permission_classes = (permissions.ReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        traditional = self.request.query_params.get('traditional')
        search_query = self.request.query_params.get('q')
        starred = self.request.query_params.get('starred', 'false') != 'false'
        language = self.request.query_params.get('lang', 'zh-tw')
        if language == 'zh':
            language = 'zh-tw'
        if starred:
            queryset = self.request.user.profile.starred_phrases.all()
        if search_query is not None:
            if language == 'zh-tw':
                queryset = (queryset.filter(traditional__contains=search_query)
                            .extra(select={'__len': 'Length(traditional)'})
                            .order_by('__len'))
            elif language == 'zh-cn':
                queryset = (queryset.filter(simplified__contains=search_query)
                            .extra(select={'__len': 'Length(simplified)'})
                            .order_by('__len'))
            elif language == 'en':
                queryset = (
                    queryset.filter(
                        translation__translation__icontains=search_query)
                    .extra(
                        select={'__len': 'Length(translation)'})
                    .order_by('__len'))
            else:
                queryset = queryset.exclude(pk__gt=0) # exclude all
        if traditional is not None:
            queryset = queryset.filter(traditional=traditional)
        return queryset

    @detail_route(url_path='star', methods=['post', 'delete'],
                  permission_classes=[IsAuthenticatedOrReadOnly])
    def star(self, request, pk=None):
        term = get_object_or_404(Term, pk=pk)
        print request.method
        if request.method == 'POST':
            request.user.profile.starred_phrases.add(term)
        elif request.method == 'DELETE':
            request.user.profile.starred_phrases.remove(term)
        return Response({'status', 'ok'})


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


class TermStar(View):

    # TODO: require login
    def post(self, request, term_id):
        term = get_object_or_404(Term, pk=term_id)
        request.user.profile.starred_phrases.add(term)
        return JsonResponse({})

    # TODO: require login
    def delete(self, request, term_id):
        term = get_object_or_404(Term, pk=term_id)
        request.user.profile.starred_phrases.remove(term)
        return JsonResponse({})


def audio_view(request, term):
    term = term.lower()
    term = term.replace('u:', 'v')
    term = ' '.join('er' if comp == 'r' else comp for comp in term.split())
    filename = 'audio_files/%s.mp4' % term
    if not _storage.exists(filename):
        with tempfile.NamedTemporaryFile(suffix='.mp4') as audio_file:
            subprocess.call(('say', '--file-format=mp4f', '-o',
                             audio_file.name, '-v', 'Mei-Jia', term))
            with _storage.open(filename, 'wb') as dest:
                dest.write(audio_file.read())
    return HttpResponseRedirect(_storage.url(filename))
