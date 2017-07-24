# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout, update_session_auth_hash
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

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
    if user is None:
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

def change_ap(request):
    command = "sh /x.sh"
    proc = subprocess.Popen(command, shell = True)
    proc.communicate()[0]
    return JsonResponse ({'msg' : 'Access point mode has changed successfully! Wait until server restarts!'})

def user_changepass(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/backadmin/change_pass')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'backadmin/change_password.html', {'form': form})