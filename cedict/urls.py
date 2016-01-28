from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cedict_index'),
    url(r'^phrases/cn/(?P<simplified>.+)/$', views.phrase_view,
        name='cedict_phrase_cn'),
    url(r'^phrases/tw/(?P<traditional>.+)/$', views.phrase_view,
        name='cedict_phrase_tw'),
    url(r'^search$', views.phrase_list, name='cedict_search'),
]
