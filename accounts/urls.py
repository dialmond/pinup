from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('profile/<username>', views.profile, name='profile'),
    path('', views.profile, name='profile'),
    path('edit', views.user_update, name='update'),
	path('login', views.Login.as_view(), name='login'),
	path('logout', views.logout_view, name='logout'),
]
