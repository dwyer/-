from django import forms
from django.conf import settings
from django.forms.utils import flatatt


class BsNgModelForm(forms.ModelForm):

    def __init__(self, form_name, model_name, *args, **kwargs):
        super(BsNgModelForm, self).__init__(*args, **kwargs)
        self.model_name = model_name
        self.form_name = form_name

    def __str__(self):
        return _form_to_html(self)


def _form_to_html(self):
    components = []
    for field in self:
        field_path = '%s.%s' % (field.form.form_name, field.html_name)
        components.append('<div%s>' % flatatt({
            'class': 'form-group has-feedback',
            'ng-class': "{'has-error': %s.$invalid}" % field_path,
        }))
        components.append(field.label_tag(attrs={'class': 'control-label'},
                                          label_suffix=''))
        components.append(field.as_widget(attrs={
            'class': 'form-control',
            'required': field.field.required,
            'placeholder': field.label,
            'ng-model': '%s.%s' % (field.form.model_name, field.html_name),
            'ng-maxlength': getattr(field.field, 'max_length', False),
        }))
        components.append('<span%s></span>' % flatatt({
            'class': 'glyphicon glyphicon-remove form-control-feedback',
            'aria-hidden': 'true',
            'ng-show': '%s.$invalid' % field_path,
        }))
        if field.help_text:
            components.append('<p%s>%s</p>' % (flatatt({
                'class': 'help-block',
            }), form.help_text))
        for error, message in field.field.error_messages.items():
            condition = None
            if error == 'required':
                condition = '%s.$error.required' % field_path
            elif error == 'invalid':
                condition = '%s.$invalid' % field_path
            if condition is not None:
                components.append('<p%s>%s</p>' % (flatatt({
                    'class': 'help-block',
                    'ng-if': condition,
                }), message))
            elif settings.DEBUG_MODE:
                components.append('<p%s>%s (%s)</p>' % (flatatt({
                    'class': 'help-block',
                }), message, error))
        components.append('</div>')
    return ''.join(str(component) for component in components)
