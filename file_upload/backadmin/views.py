# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
user = None
password = None
perm_dict = None
is_auth = False
fail = False

class UserPermissions:
    def __init__(self, user):
        self.permissions = user.permission.get_permissions()

    def get_permissions(self):
        return self.permissions


def index(request):
	context = {}
	global fail
	if fail:
		context = {'invalid' : 'Invalid username and/or password'}
	return render(request, 'backadmin/LOGIN.html', context)

def verify(request):
	flag = 'FAKE'
	global is_auth, user, password, perm_dict
	try:
		user = User.objects.get(username = request.POST.get('email', None))
		password = request.POST.get('password', None)
		flag = 'REAL'
	except User.DoesNotExist:
		pass
	if ((flag == 'REAL') and user.check_password(password)):
		perm_dict = UserPermissions(user)
		is_auth = True
		return HttpResponseRedirect('/upload/new/')
	global fail
	fail = True	
	return HttpResponseRedirect('../')

def return_permissions(request):
    print 'User is ' + str(user)
    if user is None:
        print 'User illa'
        return JsonResponse({'user_name':'_null_'})
    try:
        perms = perm_dict.get_permissions()
    except:
        pass
    perms['superuser_tasks'] = user.is_superuser
    perms['user_name'] = user.username
    return JsonResponse(perms)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('../')
