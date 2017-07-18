from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.display, name="displayyy"),
	url(r'^update_data', views.update_data, name="update_data"),
	]