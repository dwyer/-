from django.conf.urls import url

import audio.views

urlpatterns = [
    url(r'^(.+)\.mp4', audio.views.audio_view, name='audio_view'),
]
