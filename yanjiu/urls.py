from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

import audio.views
import cedict.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', cedict.views.index, name='cedict_index'),
    url(r'^phrases/cn/(?P<simplified>.+)/$', cedict.views.phrase_view,
        name='cedict_phrase_cn'),
    url(r'^phrases/tw/(?P<traditional>.+)/$', cedict.views.phrase_view,
        name='cedict_phrase_tw'),
    url(r'^search$', cedict.views.phrase_list, name='cedict_search'),
    url(r'^random$', cedict.views.random_phrase, name='cedict_random'),
    url(r'^audio/', include('audio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
