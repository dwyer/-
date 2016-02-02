from django.contrib.auth.models import User

from rest_framework import serializers

from cedict.models import Phrase, Translation
from texts.models import Text


class _BaseSerializer(serializers.HyperlinkedModelSerializer):

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


class PhraseSerializer(_BaseSerializer):
    translations = TranslationSerializer(source='translation_set', many=True)

    class Meta:
        model = Phrase
        fields = ('id', 'traditional', 'simplified', 'pinyin',
                  'pinyin_unicode', 'zhuyin', 'translations')


class TextSerializer(_BaseSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Text
        fields = ('id', 'title', 'text', 'video_url', 'owner',
                  'processed_text')
