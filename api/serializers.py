from django.contrib.auth.models import User

from rest_framework import serializers

from cedict.models import Phrase, Translation
from texts.models import Text


class TranslationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Translation
        fields = ('id', 'translation')


class PhraseSerializer(serializers.HyperlinkedModelSerializer):
    translations = TranslationSerializer(source='translation_set', many=True)

    class Meta:
        model = Phrase
        fields = ('id', 'traditional', 'simplified', 'pinyin',
                  'pinyin_unicode', 'zhuyin', 'translations')


class TextSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Text
        fields = ('id', 'title', 'text', 'video_url', 'owner')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
