from yanjiu import forms

from .models import Text


class TextForm(forms.BsNgModelForm):

    class Meta:
        model = Text
        fields = [
            'title',
            'text',
            'audio_url',
            'video_url',
        ]
