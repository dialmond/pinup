from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .models import User
from .forms import *
from .affirmations import *

import random

def profile(request):
    context = {'user': request.user, 'affirmation': random.choice(affirmations)}
    return render(request, 'accounts/profile.html', context)

def user_update(request):
    context ={}
    user = get_object_or_404(User, id=request.user.id)
    #^can we just use request.user here, or do I have to go through this?
    form = UserUpdateForm(request.POST or None, instance=user)
    form.fields['neighborhoods'].initial = user.neighborhoods.all()
    if form.is_valid():
        form.save()
        user.neighborhoods.clear()
        user.neighborhoods.add(*form.cleaned_data['neighborhoods'])
        #^since neighborhoods isn't a model field we change our many to many relationship here
        messages.success(request, 'successfully edited profile')
        return HttpResponseRedirect(reverse('accounts:profile'))

    context["form"] = form
    return render(request, "accounts/update.html", context)

class Login(LoginView):
    authentication_form=UserLoginForm
    redirect_authenticated_user = True

def logout_view(request):
    logout(request)
    messages.success(request, 'logged out')
    return HttpResponseRedirect(reverse('accounts:login'))
