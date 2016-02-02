from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from .forms import TextForm
from .models import Text


class TextList(View):

    def get(self, request):
        texts = Text.objects.all()
        # TODO: paginate
        context = {
            'texts': texts,
        }
        return render(request, 'text_list.html', context)


class TextDetail(View):

    def get(self, request, pk):
        text = get_object_or_404(Text, pk=pk)
        context = {'text': text}
        return render(request, 'text_detail.html', context)


class TextEdit(View):

    def get_text(self, request, pk):
        if pk is None:
            return None
        text = get_object_or_404(Text, pk=pk)
        if text.owner != request.user:
            raise PermissionDenied
        return text

    def get(self, request, pk=None):
        text = self.get_text(request, pk)
        form = TextForm(instance=text)
        return render(request, 'text_edit.html', {'form': form})

    def post(self, request, pk=None):
        text = self.get_text(request, pk)
        form = TextForm(request.POST, instance=text)
        if not form.is_valid():
            return render(request, 'text_edit.html', {'form': form})
        text = form.save(commit=False)
        text.owner = request.user
        text.save()
        return HttpResponseRedirect(reverse('text_detail', args=(text.pk,)))


class TextFormView(View):

    def get(self, request):
        form = TextForm('textForm', self.request.GET.get('model_name', 'text'))
        return HttpResponse(str(form))
