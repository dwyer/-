from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

import yanjiu.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', yanjiu.views.index, name='index'),
    url(r'^api/v1/', include('api.urls')),
    url(r'^audio/', include('audio.urls')),
    url(r'^cedict/', include('cedict.urls')),
    url(r'^texts/', include('texts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
