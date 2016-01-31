from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.TextList.as_view(), name='text_list'),
    url(r'^(\d+)/$', views.TextDetail.as_view(), name='text_detail'),
    url(r'^(\d+)/edit/$', views.TextEdit.as_view(), name='text_edit'),
    url(r'^new/$', views.TextEdit.as_view(), name='text_create'),
]
