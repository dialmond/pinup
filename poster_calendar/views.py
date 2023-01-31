from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import Poster
from .forms import PosterForm

# Create your views here.

class PosterIndex(generic.ListView):
    template_name = 'poster_calendar/index.html'
    #context_object_name = 'posters'
    context_object_name = 'days'

    def get_queryset(self):
        #return Poster.objects.all()
        posters = Poster.objects.all()
        days_dict = {}
        for p in posters:
           days_dict[p.take_down_date] = days_dict.get(p.take_down_date, []) + [p]
        return days_dict

class PosterCreate(SuccessMessageMixin, generic.edit.CreateView):
    model = Poster
    template_name = 'poster_calendar/form.html'
    form_class = PosterForm
    success_message = "successfully added %(poster_type)s"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            poster_type=self.object.get_poster_type_display(),
        )

    def get_success_url(self):
        return reverse('calendar:index')

class PosterUpdate(SuccessMessageMixin, generic.edit.UpdateView):
    model = Poster
    template_name = 'poster_calendar/form.html'
    form_class = PosterForm
    success_message = "successfully updated %(poster_type)s"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            poster_type=self.object.get_poster_type_display(),
        )

    def get_success_url(self):
        return reverse('calendar:index')

class PosterDelete(SuccessMessageMixin, generic.edit.DeleteView):
    model = Poster
    template_name = 'poster_calendar/delete.html'
    success_message = 'successfully deleted poster'

    def get_success_url(self):
        return reverse('calendar:index')
