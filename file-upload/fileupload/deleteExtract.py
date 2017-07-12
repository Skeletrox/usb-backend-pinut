import shutil,os
def deleteit(name_of_file):
	print name_of_file
	for filename in os.listdir("/var/www/ekstep/content"):
		if name_of_file['folder_file']==filename:
			print 'deleted file '+filename
			shutil.rmtree("/var/www/ekstep/content/"+filename)
		elif name_of_file['json_file']==filename:
			os.remove("/var/www/ekstep/content/"+filename)
				
		
