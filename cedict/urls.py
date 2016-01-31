from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^cn/(?P<simplified>.+)/$', views.phrase_view, name='cedict_phrase_cn'),
    url(r'^tw/(?P<traditional>.+)/$', views.phrase_view, name='cedict_phrase_tw'),
    url(r'^search$', views.phrase_list, name='cedict_search'),
    url(r'^random$', views.random_phrase, name='cedict_random'),
]
