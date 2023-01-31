from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from .models import User
from distribution .models import Neighborhood

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields.pop('username')


    name = forms.ModelChoiceField(queryset=User.objects.all())
    password = forms.CharField(widget=forms.PasswordInput())
    field_order=['name','password']

    def clean(self):
        name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')

        if name is not None and password:
            username = User.objects.get(name=name).username
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class UserUpdateForm(forms.ModelForm):
    neighborhoods = forms.ModelMultipleChoiceField(
        queryset=Neighborhood.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = User
        fields = ['name', 'email', 'neighborhoods']

