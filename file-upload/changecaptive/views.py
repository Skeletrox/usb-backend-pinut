from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
status_text = None
fail_text = None
def index(request):
	return render(request, 'changecaptive/change_captive.html', {'status_text': status_text, 'fail_text' : fail_text})

def write_to_file(filename, data):
	file_to_write = open('changecaptive/static/changecaptive/' + filename, 'wb+')
	file_to_write.write(data)
	file_to_write.close()

def captive_display(request):
	heading = ""
	text = ""
	heading = open('changecaptive/static/changecaptive/header.txt', 'r').read()
	text = open('changecaptive/static/changecaptive/text.txt', 'r').read()
	status_text = None
	fail_text = None
	try:
		logoexists = open('changecaptive/static/changecaptive/logo.png', 'rb')
		logo = True
	except OSError:
		logo = False
	try:
		apkexists = open('changecaptive/static/changecaptive/app.apk', 'rb')
		apk = True
	except OSError:
		apk = False
	return render(request, 'changecaptive/captiveportal.html', {'logo': logo, 'heading_text':heading, 'body_text': text, 'apk': apk, 'fail_text' : fail_text, 'status_text' : status_text})

def change_logo(request):
	if request.method == 'POST':
		write_to_file('logo.png', request.body)
	return JsonResponse({'ok':'ok'})

def change_apk(request):
	if request.method == 'POST':
		write_to_file('app.apk', request.body)
	return JsonResponse({'ok':'ok'})

def change_data(request):
	if request.method == 'POST':	
		header_data = request.POST.get('title')
		text_data = request.POST.get('description')
		if text_data is None:
			global status_text
			status_text = 'Please enter some text'
			return HttpResponseRedirect('../')
		write_to_file('text.txt', text_data)
		if header_data is not None:
			write_to_file('header.txt', header_data)
	status_text = 'ok'
	return HttpResponseRedirect('../')
