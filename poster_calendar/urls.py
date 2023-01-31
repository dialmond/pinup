from django.urls import path

from . import views

app_name = 'calendar'
urlpatterns = [
    path('', views.PosterIndex.as_view(), name='index'),
    path('add', views.PosterCreate.as_view(), name='create'),
    path('<int:pk>/edit', views.PosterUpdate.as_view(), name='update'),
    path('<int:pk>/delete', views.PosterDelete.as_view(), name='delete'),
]
