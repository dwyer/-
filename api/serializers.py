from django.contrib.auth.models import User

from rest_framework import serializers

from cedict.models import Term, Translation
from texts.models import Phrase, PhraseTag, Text


class _BaseSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(_BaseSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context:
            fields = self.context['request'].query_params.get('fields')
            if fields:
                fields = fields.split(',')
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field in existing - allowed:
                    self.fields.pop(field)


class UserSerializer(_BaseSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class TranslationSerializer(_BaseSerializer):

    class Meta:
        model = Translation
        fields = ('id', 'translation')


class TermSerializer(_BaseSerializer):
    translations = TranslationSerializer(source='translation_set', many=True)
    is_starred = serializers.SerializerMethodField('_is_starred')

    def _is_starred(self, term):
        request = self.context.get('request')
        return (request is not None
                and request.user.is_authenticated()
                and term in request.user.profile.starred_terms.all())

    class Meta:
        model = Term
        fields = ('id', 'traditional', 'simplified', 'pinyin',
                  'pinyin_unicode', 'zhuyin', 'frequency', 'translations',
                  'is_starred')



class PhraseTagSerializer(_BaseSerializer):

    class Meta:
        model = PhraseTag
        fields = (
            'name',
        )


class PhraseSerializer(_BaseSerializer):

    class Meta:
        model = Phrase
        fields = ('phrase', 'translation', 'romanization', 'level', 'due_date',
                  'updated',
                  # 'tags',
                  )

    # tags = serializers.SerializerMethodField('_tags')

    def _tags(self, phrase):
        return [tag.name for tag in phrase.phrasetag_set.all()]


class TextSerializer(_BaseSerializer):
    owner = UserSerializer(read_only=True)
    phrases = serializers.SerializerMethodField('_phrases')

    class Meta:
        model = Text
        fields = ('id', 'title', 'text', 'audio_url', 'video_url', 'owner',
                  'phrases', 'updated')

    def _phrases(self, text):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated():
            return []
        return PhraseSerializer(
            text.phrases(request.user), many=True, read_only=True).data
