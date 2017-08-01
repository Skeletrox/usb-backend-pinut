import json, os, subprocess, getpass
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
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from django.urls import reverse
from .extract import extractit
from .deleteExtract import deleteit
#<<<<<<< HEAD
from django.conf import settings
#staticFileLoc = '/file-upload/media/'
#=======

staticFileLocRoot = None

config_file = settings.CONFIG_FILE

old_files = []
files = []
total_amount = 0
total_done = 0
count = 0
is_auth = True
optional_flag = False
percentage_done = 0
perm_dict = None
user = None

class User_Permissions:
    def __init__(self, user):
        self.permissions = user.permission.get_permissions()

    def get_permissions(self):
        return self.permissions

class NoFilesError(ValueError):
    def __init__ (self, arg = None):
        self.strerror = arg
        self.args = {arg}

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('../../upload/')

def index(request):
    return render(request,'fileupload/LOGIN.html')
'''
<<<<<<< HEAD
    
=======


   

Dev's code that is not actually called in the program, can be ignored, kept for future references if needed

>>>>>>> refs/remotes/origin/master
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
<<<<<<< HEAD

'''

def verify(request, optional=False):
    flag='INIT'
    global optional_flag
    optional_flag = False
    global is_auth, user, password
    if optional:
        optional_flag = True
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
        global perm_dict
        perm_dict = User_Permissions(user)
        is_auth = True
        ############################################################
        # Load values from res.json file                           #
        ############################################################
        with open(config_file) as res_file:
            try:
                json_data = json.load(res_file)
                active_profile = json_data["active_profile"]
                staticFileLocRoot = json_data[active_profile].get("media_root", "")
               # print "staticFileLocRoot " + staticFileLocRoot
               # staticFileLocRoot = json_data["global_vars"].get("media_root", "")
            except:
                return HttpResponse("<h1>Improperly configured resources file; contact sysadmin</h1>")
        return HttpResponseRedirect('new/')    
    else:
        return render(request,'fileupload/LOGIN.html',{'invalid':'not a valid username or password',})

#=======

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
        print '-'*10 + 'WE GON EXTRACT IT YO' + '-'*10
        files = extractit(self.object.path_of_file)
        for f in files:
            obj=Content(ekfile=self.object,filename=f)
            obj.save()
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
	print data + ' omg fail '
        return HttpResponse(content=data, status=400, content_type='application/json')




class EkFileDeleteView(DeleteView):
    model = EkFile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print 'Attempting to delete ' + str(self.object)
        files = Content.objects.filter(ekfile = self.object.id)
        filename = []
        for f in files:
                filename.append(f.filename)
                f.delete()
        deleteit(filename)
        #deleteit({'folder_file':content_object.folder_file,'json_file':content_object.json_file})
        #content_object.delete()
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
        local_files_dir = '/' + getpass.getuser() + '/FILES/'
        if os.geteuid() != 0:   #If not root, user location is /home/user/files
            local_files_dir = '/home/' + getpass.getuser() + '/FILES/'
	print local_files_dir
        local_files = []
        for root, folders, files in os.walk(local_files_dir):
            for file in files:
                if (not os.path.isdir(file)) and file.endswith(".json"):
                    local_files.append(os.path.join(root, file))
	print local_files
        actual_index = local_files[0].split('/').index('FILES') + 1
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


def split_dirs(text): #Splits the entire path to get the file name
    splitty = text.split('/')
    value = splitty[len(splitty) - 1]
    return value

def transfer(request):
    try:
        if not is_auth:
            return HttpResponse("Please access this URL properly")
        elif request.method == 'GET' or request.method == 'POST':
            global percentage_done
            global total_amount, total_done, count, files, old_files
            files_existing = []
            if request.method == 'GET':
                new_files = attemptMount()
                if new_files is None:
                    return HttpResponseRedirect('../new')
                old_files = [fModel.file for fModel in EkFile.objects.all()]
                files = [thing for thing in new_files if split_dirs(thing) not in old_files]
                total_done = 0
                total_amount = len(files)
                fileCount = 0
            else:
                fileCount = request.POST.get("file_descriptor", "")
            download_more = True
            file_to_transfer = None
            if len(files) > 0:
                temp_value = 0
                for file in files:
                    if file != 'content.json':
                        try:
                            #Runs each time. Can be optimized further to handle JSON requests and responses
                            value = split_dirs(file)
                            x = EkFile.objects.get(file=str(value))
                        except EkFile.DoesNotExist:
                            file_size = os.stat(file).st_size
                            value = split_dirs(file)
                            fModel = EkFile(id = temp_value+1, file = str(value))
                            temp_value += 1
                            if fModel not in files_existing:
                                files_existing.append(fModel)
                try:
                    if len(files_existing) == 0:
                        raise NoFilesError('No Files')
                    file_to_transfer = files[int(fileCount)]
                    return_code = transfer_file(file_to_transfer)
                    if return_code != 0:
                        print 'USB unexpectedly removed!'
                        removeCorruptFile(file_to_transfer)
                except NoFilesError as error:
                    global optional_flag    #If a simple refresh occurs without a change in USB attached
                    if optional_flag:
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
                file_to_save = EkFile(id = count, file = value)
                file_to_save.save()
#<<<<<<< HEAD
                files2 = extractit(file_to_save.path_of_file)
                for f in files2:
                        obj=Content(ekfile=file_to_save,filename=f)
                        obj.save()
                print '[Z]Saved ' + value
                #list_of_files.append(file_to_save)
                #files.remove(file_to_transfer)
#=======
                #extractit(file_to_save.path_of_file)
            #Code above updates the file transferred list

            if (total_done <= total_amount - 1 or len(files_existing) == 0):
                #We still have files to download
                template = loader.get_template('fileupload/downloadFiles.html')
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
                optional_flag = True #Any further refreshes will not attempt to show "no new files available"
                download_more = None
                return HttpResponseRedirect('../new')
            #Code above is for final condition
        return JsonResponse({'null':'null'}) #For testing only, report if thrown anytime!
    except OSError:
        return HttpResponseRedirect('../new/');

def removeCorruptFile(file):
    global staticFileLocRoot
    delete_from_db_file  = EkFile.objects.get(split_dirs(file))
    delete_from_db_file.delete()
    sendString = "rm " + staticFileLocRoot + file
    t = subprocess.Popen(sendString)
    t.communicate()[0]
