from django.urls import path

from . import views

app_name = 'distribution'
urlpatterns = [
    path('', views.NeighborhoodIndex.as_view(), name='neighborhood_index'),
    path('data.json', views.distribution_json, name='distribution_json'),

    path('<slug:slug>', views.NeighborhoodDetail.as_view(), name='neighborhood_detail'),
    path('<slug:neighborhood>/update_assigned_members', views.update_assigned_members, name='update_assigned_members'),

    path('<slug:neighborhood>/add_area', views.area_create, name='area_create'),
    path('update_area/<int:area>', views.area_update, name='area_update'),
    path('delete_area/<int:pk>', views.AreaDelete.as_view(), name='area_delete'),

    path('<slug:neighborhood>/add_location', views.location_create, name='location_create'),
    path('add_location', views.location_create, name='location_create'),
    path('<slug:neighborhood>/<int:pk>', views.LocationDetail.as_view(), name='location_detail'),
    path('<slug:neighborhood>/<int:pk>/update', views.LocationUpdate.as_view(), name='location_update'),
    path('<slug:neighborhood>/<int:pk>/delete', views.LocationDelete.as_view(), name='location_delete'),

]
