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


#files_existing=[]
#list_of_files=[]
old_files = []
files = []
total_amount = 0
total_done = 0
count = 0
is_auth = False
percentage_done = 0

class NoFilesError(ValueError):
    def __init__ (self, arg = None):
        self.strerror = arg
        self.args = {arg}

def index(request):
    return render(request,'fileupload/LOGIN.html')

def verify(request):
    flag='INIT'
    global is_auth, user, password
    try:
        user=User.objects.get(username=request.POST['email'])
        logger = logging.getLogger(__name__)
        password=request.POST['password']
    #_,salt,hashpw=user.password.split('$')
        logger.error(request.POST['email']+","+request.POST['password']+" \n next line")
        logger.error(user.password+", username is "+user.username)
        flag='REAL'
    except User.DoesNotExist:
        flag = 'FAKE'
    if(flag == 'REAL' and user.check_password(password)):
        is_auth = True
        #return HttpResponseRedirect('new/')
        usb_checked = attemptMount()
        usb_flag = 'disabled'
        text = 'Please insert USB and login again'
        if usb_checked is not None:
            usb_flag = 'active'
            text = 'Click USB Download to download files'
        return render(request, 'fileupload/ekfile_form.html', {'usb_checked': usb_flag, 'text':text})
    else:
        return render(request,'fileupload/LOGIN.html',{'invalid':'not a valid username or password',})
        
    
    
    
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

def verify_USB(request):
    if request.type == 'GET':
        value = attemptMount()
        response_data = 'disabled'
        if value is not None:
            response_data = 'active '
        return JsonResponse({'data':response_data})

def split_dirs(text):
    splitty = text.split('/')
    value = splitty[len(splitty) - 1]
    return value

def transfer(request):
    try:
        if not is_auth:
            return HttpResponse("Please access this URL properly")
            '''
        elif percentage_done == 100:
            template = loader.get_template('fileupload/ekfile_form.html')
            return render(request, 'fileupload/ekfile_form.html', {'usb_checked': 'active', 'text' : 'Insert another USB to download files if you want'})
            '''
        elif request.method == 'GET' or request.method == 'POST':
            global percentage_done
            global total_amount, total_done, count, files, old_files
            files_existing = []
            if request.method == 'GET':
                new_files = attemptMount()
                if new_files is None:
                    return render(request, 'fileupload/ekfile_form.html', {'usb_checked': 'disabled', 'text' : 'You have removed USB, please reinsert and login again'})
                old_files = [fModel.file for fModel in EkFile.objects.all()]
                files = [thing for thing in new_files if split_dirs(thing) not in old_files]
                #old_files.extend(files)
                print '[Z] OldFiles are ' + str(old_files)
                print '[Z] Files are ' + str(files)
                total_done = 0
                total_amount = len(files)
                fileCount = 0
            else:
                fileCount = request.POST.get("file_descriptor", "")
            download_more = True
            print '[Z]################################Length of files = ' + str(len(files)) + '----------------------------------'
            print '[Z]--------------------------------Value of fileCount = ' + str(fileCount) + '----------------------------------'
            print '[Z]--------------------------------Value of totalDone = ' + str(total_done) + '----------------------------------'
            print '[Z]--------------------------------Value of totalAmount = ' + str(total_amount) + '################################'
            '''
            if fileCount is None:
                fileCount = 0
            '''

            file_to_transfer = None
            if len(files) > 0:
                temp_value = 0
                for file in files:
                    if file != 'content.json':
                        try:
                            value = split_dirs(file)
                            #fModel = EkFile(id = count+1, file = str(value))
                            print '[Z]Looking in EkFiles with file ' + value
                            x = EkFile.objects.get(file=str(value))
                            print '[Z]Duplicate found, please ignore ' + value
                            #files.remove(file)
                        except EkFile.DoesNotExist:
                            #x = '@CONST: FILEDOESNOTEXIST'
                            print 'Unique File ' + value + ' Found!'
                            file_size = os.stat(file).st_size
                            value = split_dirs(file)
                            fModel = EkFile(id = temp_value+1, file = str(value))
                            print '[Z]FModelled as ' + str(value)
                            temp_value += 1
                            if fModel not in files_existing:
                                files_existing.append(fModel)
                try:
                    if len(files_existing) == 0 and request.method == 'GET':
                        raise NoFilesError
                    file_to_transfer = files[int(fileCount)]
                    print '[Z]Attempting to transfer ' + str(file_to_transfer)
                    return_code = transfer_file(file_to_transfer)
                    if return_code != 0:
                        print 'USB unexpectedly removed!'
                        removeCorruptFile(file_to_transfer)
                except NoFilesError as error:
                    #Bug report: This thing is being thrown after downloading files? 
                    print 'Aiyappa file illa pa'
                    template = loader.get_template('fileupload/downloadFiles.html')
                    total_files_in_db = EkFile.objects.all()
                    context = {
                        'files_existing' : None,
                        'show_output' : False,
                        'percentage_done' : 0,
                        'current_count' : 0,
                        'btn_check_flag' : 'disabled',
                        'download_more' : False,
                    }
                    return HttpResponse(template.render(context, request))
                '''
                except ValueError as error:
                    print 'Code should not come here ValueError'
                    fileCount = 0
                    file_to_transfer = files[int(fileCount)]
                    return_code = transfer_file(file_to_transfer)
                    if return_code != 0:
                        print 'USB unexpectedly removed!'
                        removeCorruptFile(file_to_transfer)
                    try:
                        if fileCount == len(files):
                            raise IndexError('Ashurbanipal, the king of Assyria')
                    except IndexError:
                        print 'Yella mugithu andhre yaakappa illi barthiya neenu'
                        download_more = None
                        context = {
                          #  'list_of_files' : list_of_files,
                            'usb_mounted': True,
                            'usb_mounted_text' : 'Transfer Files From USB',
                        }
                        template = loader.get_template('fileupload/ekfile_form.html')
                        return HttpResponseRedirect('../new/')
                except IndexError as error:
                    print 'Yella mugithu aadhre code illi barabaaradu'
                    download_more = None
                    context = {
                      #  'list_of_files' : list_of_files,
                        'usb_mounted': True,
                        'usb_mounted_text' : 'Transfer Files From USB',
                    }
                    template = loader.get_template('fileupload/ekfile_form.html')
                    return HttpResponse('../new/')
                    #return HttpResponse(template.render(context, request))
                '''
                count += 1
                total_done += 1
                percentage_done = int(total_done*100/total_amount)
            #Code below updates the file transferred list
            if file_to_transfer is not None:
                value = split_dirs(file_to_transfer)
                file_size = os.stat(file_to_transfer).st_size
                file_to_save = EkFile(id = count, file = value)
                #file_to_save = File(id = current_file_id, file_link = file_to_transfer, create_date=timezone.now(), file_desc="Buenos Dias", file_size=file_size)
                file_to_save.save()
                print '[Z]Saved ' + value
                #list_of_files.append(file_to_save)
                #files.remove(file_to_transfer)
            #Code above updates the file transferred list
            #return HttpResponseRedirect('new/')

            if (total_done <= total_amount - 1 or len(files_existing) == 0):
                print '[O] We still have files to download'
                template = loader.get_template('fileupload/downloadFiles.html')
                total_files_in_db = EkFile.objects.all()
                context = {
                'files_existing' : files_existing,
                'show_output' : True,
                'percentage_done' : percentage_done,
                'current_count' : total_done,
                'btn_check_flag' : 'disabled',
                'download_more' : True,
                }
                return HttpResponse(template.render(context, request))


            #Code below is for final condition
            if total_done == total_amount and len(files_existing) > 0:
                print 'Yella mugithu'
                #old_files = files
                download_more = None
                context = {
                    #'list_of_files' : list_of_files,
                    'usb_mounted': True,
                    'usb_mounted_text' : 'Transfer Files From USB',
                }
                template = loader.get_template('fileupload/ekfile_form.html')
                return render(request, 'fileupload/ekfile_form.html', {'usb_checked': 'active', 'text' : 'Insert another USB to download files if you want'})
            #Code above is for final condition
    except OSError:
        template = loader.get_template('fileupload/ekfile_form.html')
        return render(request, 'fileupload/ekfile_form.html', {'usb_checked': 'disabled', 'text' : 'Please remove USB only after file transfer is complete'})

def removeCorruptFile(file):
    global staticFileLocRoot
    delete_from_db_file  = EkFile.objects.get(split_dirs(file))
    delete_from_db_file.delete()
    sendString = "rm " + staticFileLocRoot + file
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
           # 'list_of_files' : total_files_in_db,
            'usb_mounted': usb_mounted,
            'usb_mounted_text' : usb_mounted_text,
        }
        return HttpResponse(template.render(context, request))
