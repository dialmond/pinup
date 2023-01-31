from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib import messages

from .models import ClockOutResponse
from .forms import *
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = 'clockout/index.html'
    context_object_name = 'responses'

    def get_queryset(self):
        #return ClockOutResponse.objects.all()
        responses = ClockOutResponse.objects.all()
        responses_dict = {}
        for r in responses:
            responses_dict[r.week_number] = responses_dict.get(r.week_number, []) + [r]
        return responses_dict

def new(request):
    form = ClockOutForm(initial={
        'neighborhoods': [n.id for n in request.user.neighborhoods.all()],
        'week_number': timezone.now().isocalendar()[1],
        })
    #print(form.initial)
    if request.method == "POST":
        form = ClockOutForm(request.POST, initial={
            'neighborhoods': [n.id for n in request.user.neighborhoods.all()],
            'week_number': timezone.now().isocalendar()[1]
            })
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.save()
            form.save_m2m() #save many-to-many with commit=False

            messages.success(request, "Submitted clockout form")
            return HttpResponseRedirect(reverse('clockout:index'))
    context = {'form': form}
    return render(request, 'clockout/form.html', context)
