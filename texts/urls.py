from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^form$', views.TextFormView.as_view(), name='text_form'),
]
