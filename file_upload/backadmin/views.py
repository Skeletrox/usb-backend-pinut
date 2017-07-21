# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
user = None
password = None
perm_dict = None

class UserPermissions:
    def __init__(self, user):
        self.permissions = user.permission.get_permissions()

    def get_permissions(self):
        return self.permissions


def index(request):
	return render('backadmin/LOGIN.html', {})

def verify(request):
	flag = 'FAKE'
	global is_auth, user, password
	try:
		user = User.objects.get(username = request.POST.get('email', None))
		password = request.POST.get('password', None)
		flag = 'REAL'
	except User.DoesNotExist:
		pass
	if ((flag == 'REAL') and user.check_password(password)):
		perm_dict = UserPermissions(user)