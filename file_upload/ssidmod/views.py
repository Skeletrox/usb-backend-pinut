# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import subprocess
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from .ssid_modifier import return_value

# Create your views here.

ssid = return_value('ssid')

def modify_ssid(request):
    global ssid, password
    result = None
    if request.method == 'POST':
        new_ssid = request.POST.get('ssid_name', '')
        ap_type = request.POST.get('apselect', '')
        command = "modeChange.sh" + ' ' + ap_type + ' ' + new_ssid
        if ap_type == 'hostmode':
            password = request.POST.get('password', None)
            if len(password) >= 1:
                command += ' ' + password
        print 'We got ' + new_ssid
        t = subprocess.Popen(command, shell=True)
        print command
        t.communicate()[0]
        code = t.returncode
        if code != 0:
            return render(request, 'ssidmod/mod_ssid.html', {'result_text':'SSID modification failure!', 'ssid_name': ssid})
        return render(request, 'ssidmod/mod_ssid.html', {'result_text':'SSID modification is complete! Please restart the device to connect to the new SSID', 'ssid_name': new_ssid})
    return render(request, 'ssidmod/mod_ssid.html', {'result_text':None, 'ssid_name': ssid})

def index(request):
    return HttpResponseRedirect('modify_ssid/')
