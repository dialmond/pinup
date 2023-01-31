import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import *

class PageBaseForm(ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'protection', 'content', 'file']
        #help_texts = {'edit_summary': _('Briefly describe your changes'),}

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        slug = slugify(slug)
        if slug in ['_create', '_update', '_clone', '_move', '_history']:
            raise ValidationError(_('Slug cannot have this value. (Try using a different word, or not using an underscore at the beginning.)'))
        if len(slug)>= 1 and not slug[0].isalpha():
            raise ValidationError('The first character of a slug must be a letter character.)')
        return slug

    def clean_protection(self):
        protection = self.cleaned_data['protection']
        if protection not in ['NO', 'LO', 'NC']:
            raise ValidationError('Protection must be one of three values determined by this site. Refresh the page and try again.)')
        return protection

class PageForm(PageBaseForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields.pop('file')

class PageFileForm(PageBaseForm):
    def __init__(self, *args, **kwargs):
        super(PageFileForm, self).__init__(*args, **kwargs)
        self.fields.pop('content')
