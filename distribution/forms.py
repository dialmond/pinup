import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import *

class LocationForm(ModelForm):
    class Meta:
        model = Location
        exclude = ['created_date', 'created_by']
        widgets = {
            'lat': forms.HiddenInput(),
            'lon': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'rows':0, 'cols':0}),
            'hours': forms.Textarea(attrs={'rows':0, 'cols':0}),
        }
        #help_texts = {'edit_summary': _('Briefly describe your changes'),}

    def clean_lat(self):
        lat = self.cleaned_data['lat']
        if lat and not -180 < lat < 180:
            raise ValidationError('Invalid latitude value')
        return lat

    def clean_lon(self):
        lon = self.cleaned_data['lon']
        if lon and not -180 < lon < 180:
            raise ValidationError('Invalid longitude value')
        return lon

    def clean_area(self):
        area = self.cleaned_data.get('area')
        neighborhood = self.cleaned_data.get('neighborhood')
        if area and neighborhood and area.neighborhood != neighborhood:
            raise ValidationError('If area is present it must be in same neighborhood as neighborhood')
        return area

class NeighborhoodLocationForm(LocationForm):
    def __init__(self, *args, **kwargs):
        super(NeighborhoodLocationForm, self).__init__(*args, **kwargs)
        self.fields.pop('neighborhood')
