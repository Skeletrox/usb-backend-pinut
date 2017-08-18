# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .change_config import iter_vars, update_vars
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
varlist = None
varlist_full = None
changeable_vars=('cdn_url', 'accepted_extensions', 'config_json_name','telemetry','profile_name','usb_dir')

def load_vars():
	global varlist, changeable_vars, varlist_full
	varlist_full = iter_vars()
	message = None
	if varlist_full == None:
		message = "No JSON File!"
	elif len(varlist_full) < 1:
		varlist_full = None
		message = "No global vars in JSON File!"
	else:
		message = "ok"
	varlist={}
	for var in changeable_vars:
		varlist[var] = varlist_full[var]
	print varlist
	return {'var_dict' : varlist, 'message' : message}

def load_page(request):
	context = load_vars()
	return render(request, 'changevars/varchange.html', context)

def update_data(request):
    if request.method == 'POST':
        print 'GOT POST'
        global varlist, varlist_full
        for key in varlist:
            print "textinput-%s" %(key)
            new_val = request.POST.get("textinput-" + key, None)
            print 'Should be %s' %(new_val)
            if len(new_val) > 0:
                varlist_full[key] = new_val
        print varlist
        update_vars(varlist)
    return HttpResponseRedirect("../")
