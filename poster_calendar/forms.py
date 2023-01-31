import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Poster

class DateInput(forms.DateInput):
    input_type = 'date'

class PosterForm(ModelForm):
    class Meta:
        model = Poster
        exclude = ['created_date']
        widgets = {
            'poster_type': forms.RadioSelect(),
            'put_up_date': DateInput(),
            'take_down_date': DateInput(),
            'neighborhoods': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows':0, 'cols':0}),
        }

    def clean_take_down_date(self):
        take_down_date = self.cleaned_data['take_down_date']
        put_up_date = self.cleaned_data['put_up_date']
        if take_down_date < put_up_date:
            raise ValidationError('Take down date must be after put up date')
        return take_down_date
