from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.load_page, name="loadpage"),
	url(r'^update_data/', views.update_data, name="update_data"),
	]