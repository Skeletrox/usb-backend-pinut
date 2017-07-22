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
	var_dict = {}
	for dictionary in varlist:
		var_dict[dictionary['name']] = dictionary['value']
	return {'var_dict' : var_dict, 'message' : message}

def load_page(request):
	context = load_vars()
	return render(request, 'changevars/varchange.html', context)

def update_data(request):
	if request == 'POST':
		for key, value in varlist.items():
			new_val = request.POST.get("textinput-" + str(key), None)
			if new_val is not None:
				for dictionary in varlist:
					if dictionary['name'] == key:
						dictionary['value'] = new_val
		update_vars(varlist)
	return HttpResponseRedirect("../")