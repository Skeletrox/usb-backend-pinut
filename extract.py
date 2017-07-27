import zipfile,os,shutil

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

	#move the ecar file to ekstep file folder starting with the name do_
	for filename in os.listdir(folder):
		if(not filename.endswith(".json")):
			break

	index=file_path.rfind('/')
	file_name=file_path[index+1:]
	shutil.copy2(file_path,folder+"/"+filename+"/"+file_name)

	#change the name of manifest file to folder name
	change_name=folder[folder.rfind('/')+1:]
	
	#print change_name
	#renames the manifest file inside the ekstep file uploaded folder
	os.rename(folder+"/manifest.json",folder+"/"+change_name+".json")
	
	#list for storing the extracted items names
	content_list=[]
	
	#collects the folders and files extracted inside the content_list
	
	for filename in os.listdir(folder):
		content_list.append(filename)
		
	#print content_list

	index=file_path.find("/ecar_files")
	content_path=file_path[:index]
	content_path+="/content"

	#files list 

	#move the contents of the ekstep file uploaded folder

	for filename in os.listdir(folder):
		print filename
		if(filename.endswith(".json")):
			shutil.move(folder+"/"+filename,content_path+"/"+"json_files")
		else:
		
			try:
				shutil.move(folder+"/"+filename,content_path)
			except:
				print "This file already exists"
				break
	
	#remove's the ekstep file uploaded folder which is empty right now 
	shutil.rmtree(folder)
	#name of the folder which we got after extracting .ecar file
	return content_list
	
