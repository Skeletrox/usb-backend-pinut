from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name = 'index'),
	url(r'^modify_ssid/$', views.modify_ssid, name="modify_ssid"),
	]