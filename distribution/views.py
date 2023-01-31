from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import Neighborhood, Area, Location
from accounts.models import User
from .forms import *

# Create your views here.

class NeighborhoodIndex(generic.ListView):
    template_name = 'distribution/neighborhood_index.html'
    context_object_name = 'neighborhoods'

    def get_queryset(self):
        return Neighborhood.objects.all()

def distribution_json(request):
    json_data = {}
    neighborhoods = Neighborhood.objects.all().order_by('pk')
    for n in neighborhoods:
        n_dict = {"name": n.name, "id": n.pk}
        if n.area.all():
            #n_dict['areas'] = [{'name': a.name, 'id': a.pk} for a in n.area.all().order_by('pk')]
            n_dict['areas'] = {a.pk: {'name': a.name, 'id': a.pk} for a in n.area.all().order_by('pk')}
            #no fuckin way, you can use list compression on a dict. huh, life is good
        json_data[n.pk] = n_dict
    return JsonResponse(json_data)

class NeighborhoodDetail(generic.DetailView):
    template_name = 'distribution/neighborhood_detail.html'
    model = Neighborhood
    context_object_name = 'neighborhood'

    def get_context_data(self,*args, **kwargs):
        context = super(NeighborhoodDetail, self).get_context_data(*args,**kwargs)
        context['users'] = User.objects.all()
        context['misc_locations'] = self.object.location.filter(area=None)
        context['hasAddresses'] = Location.objects.exclude(lon__isnull=True).exclude(lat__isnull=True)
        return context

def update_assigned_members(request, neighborhood):
    neighborhood = get_object_or_404(Neighborhood, slug=neighborhood)
    try:
        user = request.POST['member']
        action = request.POST['action']
    except:
        # Redisplay the view.
        return render(request, 'distribution/neighborhood_detail.html')
    else:
        user = User.objects.get(id=user)
        try:
            if action == "add":
                neighborhood.users.add(user)
                messages.success(request, f'successfully added {user} to route')
            elif action == "remove":
                 neighborhood.users.remove(user)
                 messages.success(request, f'successfully removed {user} from route')
        except:
            pass
    return HttpResponseRedirect(reverse('distribution:neighborhood_detail', args=(neighborhood.slug,)))

def area_create(request, neighborhood):
    neighborhood = get_object_or_404(Neighborhood, slug=neighborhood)
    try:
        name = request.POST['name']
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the view.
        return render(request, 'distribution/neighborhood_detail.html')
    else:
        area = Area(name=name, neighborhood=neighborhood)
        area.save()
        messages.success(request, 'successfully created area')
        return HttpResponseRedirect(reverse('distribution:neighborhood_detail', args=(neighborhood.slug,)))

def area_update(request, area):
    area = get_object_or_404(Area, pk=area)
    try:
        new_name = request.POST['new_name']
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the view.
        return render(request, 'distribution/detail.html')
    else:
        area.name = new_name
        area.save()
        messages.success(request, 'successfully updated name of area')
        return HttpResponseRedirect(reverse('distribution:neighborhood_detail', args=(area.neighborhood.slug,)))

class AreaDelete(SuccessMessageMixin, generic.edit.DeleteView):
    model = Area
    template_name = 'distribution/area_delete.html'
    success_message = 'successfully deleted area'

    def get_success_url(self):
        return reverse('distribution:neighborhood_detail', args=(self.object.neighborhood.slug,))

class LocationDetail(generic.DetailView):
    template_name = 'distribution/location_detail.html'
    model = Location
    context_object_name = 'location'

def location_create(request, neighborhood=None):
    if neighborhood:
        neighborhood = get_object_or_404(Neighborhood, slug=neighborhood)
        form = NeighborhoodLocationForm(request.POST or None)
        form.fields['area'].queryset = Area.objects.filter(neighborhood=neighborhood)
        #^filter to areas only in this neighborhood
        form.initial = {'area': request.GET.get('area')}
    else:
        form = LocationForm(request.POST or None)
        user_neighborhoods = request.user.neighborhoods
        form.neighborhood.queryset = sorted(Neighborhood.objects.all, key = lambda x: x in user_neighborhoods)
        #^sort where if a neighborhood is a user's, it should be first

    if form.is_valid(): #success, set user and save
        location = form.save(commit=False)
        if neighborhood:
            location.neighborhood = neighborhood
        location.created_by = request.user
        location.save()
        messages.success(request, "successfully added location %s" %(location.name))
        return HttpResponseRedirect(reverse('distribution:location_detail', kwargs={'neighborhood': location.neighborhood.slug, 'pk': location.id}))
    elif request.POST:
        messages.error(request, "please correct the errors listed")

    context = {'form': form, 'neighborhood': neighborhood, 'create': True}
    return render(request, 'distribution/location_form.html', context)

class LocationUpdate(SuccessMessageMixin, generic.edit.UpdateView):
    model = Location
    template_name = 'distribution/location_form.html'
    success_message = 'successfully updated location'
    form_class = LocationForm

    def get_context_data(self,*args, **kwargs):
        context = super(LocationUpdate, self).get_context_data(*args,**kwargs)
        context['neighborhood'] = self.object.neighborhood #supply this context for form
        context['update'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('distribution:location_detail', kwargs={'neighborhood': self.object.neighborhood.slug, 'pk': self.object.id})

class LocationDelete(SuccessMessageMixin, generic.edit.DeleteView):
    model = Location
    template_name = 'distribution/location_delete.html'
    success_message = 'successfully deleted location'

    def get_success_url(self):
        return reverse('distribution:neighborhood_detail', kwargs={'slug': self.object.neighborhood.slug})
