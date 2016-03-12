from yanjiu import forms

from .models import Text


class TextForm(forms.BsNgModelForm):

    class Meta:
        model = Text
        fields = [
            'title',
            'audio_url',
            'video_url',
            'text',
        ]
