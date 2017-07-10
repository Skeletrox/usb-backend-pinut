# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from .ssid_modifier import change_manually, return_value

# Create your views here.

ssid = return_value('ssid')
password = return_value('password')

def modify_ssid(request):
    global ssid, password
    result = 'dog'
    if request.method == 'POST':
        new_ssid = request.POST.get('ssid_name', '')
        print 'We got ' + new_ssid
        new_password = request.POST.get('ssid_password', '')
        new_password_2 = request.POST.get('ssid_password_2', '')
        print 'We got ' + new_password
        if new_password != new_password_2:
            return render(request, 'ssidmod/mod_ssid.html', {'result_text':'Passwords do not match!', 'ssid_name': ssid, 'password_name': password})
        if len(new_ssid) > 0:
            result = change_manually('ssid', new_ssid)
        if len(new_password) > 8 and result == 0:
            result = change_manually('wpa_passphrase', new_password)
        if type(result) is not int:
            return render(request, 'ssidmod/mod_ssid.html', {'result_text':'Please enter a valid value', 'ssid_name': ssid, 'password_name': password})
        if result == 0:
            ssid = new_ssid
            password = new_password
            return render(request, 'ssidmod/mod_ssid.html', {'result_text':'SSID modification is complete! Please reconnect if required', 'ssid_name': ssid, 'password_name': password})
        return render(request, 'ssidmod/mod_ssid.html', {'result_text':'SSID modification failure!', 'ssid_name': ssid, 'password_name': password})
    return render(request, 'ssidmod/mod_ssid.html', {'result_text':None, 'ssid_name': ssid, 'password_name': password})
def index(request):
    return HttpResponseRedirect('modify_ssid/')