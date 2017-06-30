import json, os, subprocess
import logging

from .USBFinder import attemptMount,transfer_file
from hashlib import sha1
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render,get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView
from .models import EkFile
from django.contrib.auth.models import User
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from django.urls import reverse

staticFileLoc = '/Programming/Scratch/file-upload-master/file-upload/file-upload/media/'
staticFileLocRoot ='/home/'+'skeletrox'+staticFileLoc


files_existing=[]
list_of_files=[]
files = []
total_amount = 0
total_done = 0
count = 0

def index(request):
    return render(request,'fileupload/LOGIN.html')

def verify(request):
    user=User.objects.get(username=request.POST['email'])
    logger = logging.getLogger(__name__)
    password=request.POST['password']
    #_,salt,hashpw=user.password.split('$')
    logger.error(request.POST['email']+","+request.POST['password']+" \n next line")
    logger.error(user.password+", username is "+user.username)
    if(user is not None and user.check_password(password)):
        return HttpResponseRedirect('new/')
    else:
        return render(request,'fileupload/LOGIN.html',{'invalid':'not a valid username or password'})
        
    
    
    
class EkFileCreateView(CreateView):
    model = EkFile
    fields = "__all__"

    def form_valid(self, form):
        
        self.object = form.save()
        print self.object
        files = [serialize(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        print 'Before you send post request'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


#class BasicPlusVersionCreateView(EkFileCreateView):
 #   template_name_suffix = '_basicplus_form'


class EkFileDeleteView(DeleteView):
    model = EkFile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class EkFileListView(ListView):
    model = EkFile
    
    def render_to_response(self, context, **response_kwargs):
        files = [ serialize(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
 

def transfer(request):
    if request.method == 'GET' or request.method == 'POST':
        global files_existing, files, total_amount, list_of_files
        if request.method == 'GET':
            files = attemptMount()
            print 'Files are ' + str(files)
            total_amount = len(files)
        global total_done
        global count
        download_more = True
        fileCount = request.POST.get("file_descriptor", "")
        if fileCount is None:
            fileCount = 0
        file_to_transfer = None
        if len(files) > 0:
            for file in files:
                if file != 'content.json':
                    print 'Looking in EkFiles with file ' + file 
                    try:
                        x =  EkFile.objects.get(file=file)
                    except EkFile.DoesNotExist:
                        x = None
                        print 'Unique File Found!'
                    if x == None:
                        file_size = os.stat(file).st_size
                        fModel = EkFile(id = count+1, file = file)
                    #fModel = File(id = count +1, file_link = file, create_date=timezone.now(), file_desc="Buenos Dias", file_size=file_size)
                        count += 1
                    #fModel.save()
                        files_existing.append(fModel)
            try:
                file_to_transfer = files[int(fileCount)]
                print 'Attempting to transfer ' + str(file_to_transfer)
                return_code = transfer_file(file_to_transfer)
                if return_code != 0:
                    print 'USB unexpectedly removed!'
                    removeCorruptFile(file_to_transfer)
            except ValueError as error:
                fileCount = 0
                file_to_transfer = files[int(fileCount)]
                return_code = transfer_file(file_to_transfer)
                if return_code != 0:
                    print 'USB unexpectedly removed!'
                    removeCorruptFile(file_to_transfer)
            except IndexError as error:
                download_more = None
                context = {
                    'list_of_files' : list_of_files,
                    'usb_mounted': True,
                    'usb_mounted_text' : 'Transfer Files From USB',
                }
                template = loader.get_template('fileupload/ekfile_form.html')
                return HttpResponseRedirect('../new/')
        current_file_id = len(EkFile.objects.all())
        total_done += 1
        percentage_done = int(total_done*100/total_amount)
        #Code below updates the file transferred list
        if file_to_transfer is not None:
            file_size = os.stat(file_to_transfer).st_size
            file_to_save = EkFile(id = current_file_id, file = file_to_transfer)
            #file_to_save = File(id = current_file_id, file_link = file_to_transfer, create_date=timezone.now(), file_desc="Buenos Dias", file_size=file_size)
            file_to_save.save()
            list_of_files.append(file_to_save)
        #Code above updates the file transferred list
        #return HttpResponseRedirect('new/')
        template = loader.get_template('fileupload/downloadFiles.html')
        total_files_in_db = EkFile.objects.all()
        context = {
        'files_existing' : files_existing,
        'show_output' : download_more,
        'percentage_done' : percentage_done,
        'current_count' : total_done,
        'btn_check_flag' : 'disabled',
        'download_more' : download_more,
        }
        return HttpResponse(template.render(context, request))
    return HttpResponse("Please access this URL properly")

def removeCorruptFile(file):
    global staticFileLocRoot
    sendString = "rm " + staticFileLocRoot + "/" + file
    t = subprocess.Popen(sendString)
    t.communicate()[0]

def delete_all(request):
    if request.method=='POST':
        ek_files = EkFile.objects.all()
        for ek_file in ek_files:
            ek_file.delete()
        template = loader.get_template('checkUpdates/ekfile_form.html')
        total_files_in_db = EkFile.objects.all()
        context = {
            'list_of_files' : total_files_in_db,
            'usb_mounted': usb_mounted,
            'usb_mounted_text' : usb_mounted_text,
        }
        return HttpResponse(template.render(context, request))























'''
def transfer(request):
    files=[]
    #Returns list of files that correspond to requirements
    files=attemptMount()
    files_existing=[]
    unique_files_existing=[]
    unique_files=[]
    if files is not None:
        unique_files  = [file for file in files if file not in files_existing_names]
    else:
        unique_files = None
    total_done = 0
    if unique_files is not None:
        for file1 in unique_files:
            if file1 != 'content.json':
                try:
                    x =  File.objects.get(file_link=file)
                except File.DoesNotExist:
                    x = None
                if x == None:

                    fModel = EkFile(file = file1)
                    fModel.save()
                    unique_files_existing.append(fModel)
    files_existing.append(unique_files_existing)
    files_existing_names.append(unique_files)
    if request.method == 'GET':
            unique_files_existing
            total_amount = len(files)
            download_more = True
            fileCount = request.POST.get("file_descriptor", "")
            try:
                return_code = transfer_file(files[int(fileCount)])
                if return_code != 0:
                    print ('USB unexpectedly removed!')
                    return HttpResponse(content=data, status=400, content_type='application/json')
            except IndexError as error:                                         #Thrown when there are no more files to #download 
                download_more = None
            total_done += 1
            percentage_done = int(total_done*100/total_amount)
            template = loader.get_template('checkUpdates/downloadFiles.html')
            context = {
            'files_existing' : unique_files_existing,
            'show_output' : download_more,
            'percentage_done' : percentage_done,
            'current_count' : total_done,
            'btn_check_flag' : 'disabled',
            'download_more' : download_more,
            }
            return HttpResponseRedirect('new/')
    return HttpResponse("Please access this URL properly")
'''    

