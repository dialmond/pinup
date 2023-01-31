from django import forms
from .models import ClockOutResponse

class ClockOutForm(forms.ModelForm):
    class Meta:
        model = ClockOutResponse
        exclude = ['user', 'submitted']
        widgets = {
            'neighborhoods': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows':0, 'cols':0}),
	    }

