from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^phrases/(\d+)/star$', views.ApiPhrasesStar.as_view()),
    url(r'^phrases/(.+)$', views.ApiPhrase.as_view()),
]
