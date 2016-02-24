from django.http import HttpResponse
from django.views.generic import View

from .forms import TextForm


class TextFormView(View):

    def get(self, request):
        form = TextForm('textForm', self.request.GET.get('model_name', 'text'))
        return HttpResponse(str(form))
