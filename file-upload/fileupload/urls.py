
from django.conf.urls import url
from fileupload.views import (
        #BasicPlusVersionCreateView,
        EkFileCreateView, EkFileDeleteView, EkFileListView,
        )
from . import views

app_name='fileupload'
urlpatterns = [
    #url(r'^basic/plus/$', BasicPlusVersionCreateView.as_view(), name='upload-basic-plus'),
    url(r'^new/$', EkFileCreateView.as_view(), name='upload-new'),
    url(r'^delete/(?P<pk>\d+)$', EkFileDeleteView.as_view(), name='upload-delete'),
    url(r'^view/$', EkFileListView.as_view(), name='upload-view'),
    url(r'^$',views.index,name='index'),
    url(r'^verify$',views.verify,name='verify'),
    url(r'^transfer/$', views.transfer, name="transfer"),
]
