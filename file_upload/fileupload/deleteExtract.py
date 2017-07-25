import shutil,os,sys,json

sys.path.append("/home/pi/usb-backend-pinut/file_upload/")
os.environ['DJANGO_SETTINGS_MODULE']='file-upload.settings'
import django
from django.http import HttpResponse
from django.conf import settings

config_file = settings.CONFIG_FILE

def deleteit(files):    
        print files
        with open(config_file) as res_file:
            try:
                json_data = json.load(res_file)
                active_profile = json_data["active_profile"]
                content_path = json_data[active_profile].get("unzip_content", "")
                json_dir_path = json_data[active_profile].get("json_dir", "")
            except:
                return HttpResponse("<h1>Improperly configured resources file; contact sysadmin</h1>")

        for filename in os.listdir(content_path):
                if filename in files:
                        print 'deleted folder '+filename
                        files.remove(filename)
                        shutil.rmtree(content_path+filename)
        
        
        print files             
        
        #removing the .json files
        for filename in os.listdir(json_dir_path):
                if filename in files:
                        print 'deleted file '+filename
                        files.remove(filename)
                        os.remove(json_dir_path+filename)
