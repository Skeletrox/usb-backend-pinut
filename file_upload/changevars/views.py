# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .change_config import iter_vars, update_vars
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
varlist = None

def load_vars():
	global varlist
	varlist = iter_vars()
	message = None
	if varlist == None:
		message = "No JSON File!"
	elif len(varlist) < 1:
		varlist = None
		message = "No global vars in JSON File!"
	else:
		message = "Loaded variables!"
	print varlist
	return {'var_dict' : varlist, 'message' : message}

def load_page(request):
	context = load_vars()
	return render(request, 'changevars/varchange.html', context)

def update_data(request):
    if request.method == 'POST':
        print 'GOT POST'
        global varlist
        for key, value in varlist:
            print "textinput-%s" %(key)
            new_val = request.POST.get("textinput-" + key, None)
            print 'Should be %s' %(new_val)
            if len(new_val) > 0:
                varlist[key] = new_val
        print varlist
        update_vars(varlist)
    return HttpResponseRedirect("../")
