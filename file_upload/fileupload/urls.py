
from django.conf.urls import url
from fileupload.views import (
        #BasicPlusVersionCreateView,
        EkFileCreateView, EkFileDeleteView, EkFileListView,
        )
from . import views

app_name='fileupload'
urlpatterns = [
    url(r'^new/$', EkFileCreateView.as_view(), name='upload-new'),
    url(r'^delete/(?P<pk>\d+)$', EkFileDeleteView.as_view(), name='upload-delete'),
    url(r'^view/$', EkFileListView.as_view(), name='upload-view'),
    url(r'^$',views.index,name='index'),
    url(r'^transfer/$', views.transfer, name="transfer"),
    url(r'^verify_USB/$', views.verify_USB, name="verifyusb"),
    url(r'^user_logout/$', views.user_logout, name='userlogout'),
    url(r'^download_to_usb/$', views.download_to_USB, name='downloadtousb'),
    url(r'^create_file/$', views.createFile, name="createfile"),
]
