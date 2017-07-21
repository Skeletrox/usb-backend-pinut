from django.conf.urls import url
from . import views

app_name = "backadmin"
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^verify/', views.verify, name='verify'),
	url(r'^return_permissions/', views.return_permissions, name="return_permissions"),
	url(r'^user_logout/', views.user_logout, name="user_logout")
]