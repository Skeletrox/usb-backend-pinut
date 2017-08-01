import zipfile,os,shutil,sys,json

sys.path.append("/home/pi/usb-backend-pinut/file_upload/")
os.environ['DJANGO_SETTINGS_MODULE']='file-upload.settings'
import django
from django.http import HttpResponse
from django.conf import settings

config_file = settings.CONFIG_FILE

def extractit(path_of_file):

    #ekstep file uploaded path obtained using file.path
        file_path=path_of_file

        zip_ref=zipfile.ZipFile(file_path,'r')

        index=file_path.find(".ecar")

        #folder name
        folder=file_path[:index]


        #create a folder for the ekstep file uploaded uisng its own name
        os.makedirs(folder)

        #ekstep file uploaded folder which contains the unzip version of the ekstep file uploaded
        zip_ref.extractall(folder)
        zip_ref.close()
        '''
        #move the ecar file to ekstep file folder starting with the name do_
        for filename in os.listdir(folder):
                if(not filename.endswith(".json")):
                        break

        index=file_path.rfind('/')
        file_name=file_path[index+1:]
        shutil.copy2(file_path,folder+"/"+filename+"/"+file_name)


        #change the name of manifest file to folder name
        change_name=folder[folder.rfind('/')+1:]
        '''        
        #renames the manifest file inside the ekstep file uploaded folder 

        index=file_path.rfind('/')
        file_name=file_path[index+1:]
        os.rename(folder+"/manifest.json",folder+"/"+file_name+".json")

        #list for storing the extracted items names
        content_list=[]

        #collects the folders and files extracted inside the content_list

        for filename in os.listdir(folder):
            content_list.append(filename)

        #print content_list

        with open(config_file) as res_file:
            try:
                json_data = json.load(res_file)
                active_profile = json_data["active_profile"]
                content_path = json_data[active_profile].get("unzip_content", "")
                json_dir_path = json_data[active_profile].get("json_dir", "")
            except:
                return HttpResponse("<h1>Improperly configured resources file; contact sysadmin</h1>")
        if not os.path.exists(content_path):
            os.makedirs(content_path)               
        if not os.path.exists(json_dir_path):
            os.makedirs(json_dir_path)

        #files list 

        #move the contents of the ekstep file uploaded folder

        for filename in os.listdir(folder):
            if(filename.endswith(".json")):
                shutil.move(folder+"/"+filename,json_dir_path)
            else:
                try:
                    shutil.move(folder+"/"+filename,content_path)
                except:
                    print "This file already exists"
                    #break

        #remove's the ekstep file uploaded folder which is empty right now 
        shutil.rmtree(folder)
        #name of the folder which we got after extracting .ecar file
        return content_list   
