# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout, update_session_auth_hash, authenticate, login
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

# Create your views here.
user_str = None
password = None
perm_dict = None
is_auth = False
fail = False
user = None

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
    global is_auth, user_str, password, perm_dict, user
    try:
        user_str = User.objects.get(username = request.POST.get('email', None))
        password = request.POST.get('password', None)
        flag = 'REAL'
    except User.DoesNotExist:
        pass
    if ((flag == 'REAL') and user_str.check_password(password)):
        perm_dict = UserPermissions(user_str)
        is_auth = True
        user = authenticate(username = user_str.username, password = password)
        if user is None:
            return HttpResponseRedirect('../')
        if user.is_active:
            login(request, user)
        return HttpResponseRedirect('/upload/new/')
    global fail
    fail = True 
    return HttpResponseRedirect('../')

def return_permissions(request):
    global user
    if user is None:
        return JsonResponse({'user_name':'_null_'})
    try:
        perms = perm_dict.get_permissions()
    except:
        pass
    perms['superuser_tasks'] = user_str.is_superuser
    perms['user_name'] = user_str.username
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
            update_session_auth_hash(request, user)
            return HttpResponseRedirect('/backadmin/change_pass')
        else:
            print 'FAIL'
            return HttpResponseRedirect('/backadmin/change_pass')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'backadmin/change_password.html', {'form': form})