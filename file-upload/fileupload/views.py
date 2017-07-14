import json, os, subprocess, getpass, io
import logging

from .USBFinder import attemptMount,transfer_file, get_usb_name
from hashlib import sha1
from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import Context, loader
from django.shortcuts import render,get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView
from .models import EkFile, Content
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from django.urls import reverse
from .extract import extractit
from .deleteExtract import deleteit

#staticFileLoc = '/file-upload/media/'
staticFileLocRoot = None
telemetryLocRoot = None


#files_existing=[]
#list_of_files=[]
old_files = []
files = []
total_amount = 0
total_done = 0
count = 0
is_auth = False
optional_flag = False
percentage_done = 0

class NoFilesError(ValueError):
    def __init__ (self, arg = None):
        self.strerror = arg
        self.args = {arg}

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('../../upload/')

def index(request):
    return render(request,'fileupload/LOGIN.html')
    
@ensure_csrf_cookie
def upload(request):
    if request.method=='POST':
        instance=EkFile(file=request.FILES['files'])
        obj=instance.save();
        print (instance)
        values=serialize(instance)
        data={"files":values}
        response=json.dumps(data)
        print (response)
        if instance.type_of_file=="ecar":
        	print instance.path_of_file
        	files=extractit(instance.path_of_file)
        	instance=Content(ekfile=instance,folder_file=files,json_file=files+".json")
        	instance.save()
        return HttpResponse(response,content_type="application/json")
        
@ensure_csrf_cookie
def list_the_files(request):
    values=[serialize(instance) for instance in EkFile.objects.all()]
    data={"files":values}
    response=json.dumps(data)
    print (response)
    return HttpResponse(response,content_type="application/json")
    
@ensure_csrf_cookie
def delete_files(request):
    print ("Delete this file: "+request.POST['id'])
    instance=EkFile.objects.get(id=request.POST['id'])
    print (instance)
    if instance.type_of_file=="ecar":
    	obj=Content.objects.get(ekfile=instance.id)
    	deleteit({'folder_file':obj.folder_file,'json_file':obj.json_file})
    	obj.delete()
    instance.delete()
    return HttpResponse(json.dumps({"id":4}),content_type="application/json")

def verify(request, optional=False):
    flag='INIT'
    global optional_flag
    optional_flag = False
    global is_auth, user, password
    if optional:
        optional_flag = True
        usb_checked = attemptMount()
        usb_flag = 'disabled'
        text = 'Please insert USB and refresh   '
        return HttpResponseRedirect('../new')
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
        ############################################################
        # Load values from res.json file                           #
        ############################################################
        with open('support_files/res.json') as res_file:
            try:
                json_data = json.load(res_file)
                staticFileLocRoot = json_data["global_vars"][0].get("value", "")
                telemetryLocRoot = json_data["global_vars"][1].get("value", "")
            except:
                return HttpResponse("<h1>Improperly configured resources file; contact sysadmin</h1>")
        return HttpResponseRedirect('new/')    
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
        print self.object.path_of_file
        extractit(self.object.path_of_file)
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
	print data + ' omg fail '
        return HttpResponse(content=data, status=400, content_type='application/json')


#class BasicPlusVersionCreateView(EkFileCreateView):
 #   template_name_suffix = '_basicplus_form'


class EkFileDeleteView(DeleteView):
    model = EkFile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print 'Attempting to delete ' + str(self.object)
        content_object = Content.objects.get(ekfile = self.object)
        deleteit({'folder_file':content_object.folder_file,'json_file':content_object.json_file})
        content_object.delete()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

def delete_all(request):
    if request.method == 'POST':
        EkFile.objects.all().delete()
        return HttpResponseRedirect('../new/')
    return HttpResponse('Kaiko aise karta ba tu')


class EkFileListView(ListView):
    model = EkFile
    
    def render_to_response(self, context, **response_kwargs):
        files = [ serialize(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

def verify_USB(request):
    value = attemptMount()
    response_data = 'disabled'
    response_text = 'Please insert USB and refresh'
    if value is not None:
        response_data = 'active '
        response_text = 'Click USB Upload to upload files'
    return JsonResponse({'data':response_data, 'usb_text' : response_text})

def download_to_USB(request):
    usb_name = get_usb_name()
    if usb_name is not None:
        local_files_dir = '/' + getpass.getuser() + telemetryLocRoot
        if os.geteuid() != 0:
            local_files_dir = '/home/' + getpass.getuser() + telemetryLocRoot
	    print local_files_dir
        local_files = []
        for root, folders, files in os.walk(local_files_dir):
            for file in files:
                if (not os.path.isdir(file)) and file.endswith(".json"):
                    local_files.append(os.path.join(root, file))
	    print local_files
        if len(local_files < 1):
            return JsonResponse({'res':'No supported local files available'})
        actual_index = local_files[0].split('/').index(split_dirs(telemetryLocRoot)) + 1
        for file in local_files:
            os.chdir('/media/' + getpass.getuser() + '/' + usb_name)
            split_list = file.split('/')
            for i in range (actual_index, len(split_list) - 1):
                if not os.path.exists(split_list[i]):
                    os.makedirs(split_list[i])
                os.chdir(split_list[i])
            command = 'cp "' + file + '" "' + os.getcwd() + '"'
            t = subprocess.Popen(command, shell=True)
            t.communicate()[0]
            result = t.returncode
            if result != 0:
                return JsonResponse ({'res': 'Copy aborted! [USB Unplugged/Insufficient Space?]'})
        return JsonResponse({'res': 'Copy successful'})
    return JsonResponse({'res':'Reinsert USB'})


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
                    if len(files_existing) == 0:
                        raise NoFilesError('Maria Theresa')
                    file_to_transfer = files[int(fileCount)]
                    print '[Z]Attempting to transfer ' + str(file_to_transfer)

                    return_code = transfer_file(split_dirs(file_to_transfer))
                    if return_code != 0:
                        print 'USB unexpectedly removed!'
                        removeCorruptFile(file_to_transfer)
                except NoFilesError as error:
                    #Bug report: This thing is being thrown after downloading files? 
                    print 'Aiyappa file illa pa'
                    global optional_flag
                    if optional_flag:
                        usb_checked = attemptMount()
                        usb_flag = 'disabled'
                        text = 'Please insert USB and refresh   '
                        return HttpResponseRedirect('../new')
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
                count += 1
                total_done += 1
                percentage_done = int(total_done*100/total_amount)
            #Code below updates the file transferred list
            if file_to_transfer is not None:
                value = split_dirs(file_to_transfer)
                file_size = os.stat(file_to_transfer).st_size
                file_to_save = EkFile(id = count, file = value)
                #file_to_save = File(id = current_file_id, file_link = file_to_transfer, create_date=timezone.now(), file_desc="Buenos Dias", file_size=file_size)
                print '[Z]About to save ' + value
                file_to_save.save()
                extractit(file_to_save.path_of_file)
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
                global optional_flag
                optional_flag = True
                download_more = None
                return HttpResponseRedirect('../new')
            #Code above is for final condition
        return JsonResponse({'null':'null'})
    except OSError:
        return HttpResponseRedirect('../new/');

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
