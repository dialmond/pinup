from django.urls import path, register_converter

from . import views, converters
register_converter(converters.PathConverter, 'page')

app_name = 'wiki'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
	path('_create', views.create, name='create'),
	path('_upload', views.upload, name='upload'),
	path('<page:page_path>', views.detail, name='detail'),
	path('<page:page_path>/_create', views.create, name='create'),
	path('<page:page_path>/_upload', views.upload, name='upload'),
	path('<page:page_path>/_update', views.update, name='update'),
	path('<page:page_path>/_delete', views.delete, name='delete'),
	path('<page:page_path>/_revert/<int:edit_number>', views.revert, name='revert'),
	path('<page:page_path>/_history', views.history, name='history'),

	#path('<page:page_path>/_move', views.page_move, name='page_move'),
	#path('<page:page_path>/_clone', views.page_clone, name='page_clone'),
	#path('<page:page_path>/_source', views.page_source, name='page_source'),
]
