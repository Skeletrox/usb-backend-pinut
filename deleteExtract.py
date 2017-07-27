import shutil,os
def deleteit(files):	
	print files
	for filename in os.listdir("/var/www/ekstep/content"):
		if filename in files:
			print 'deleted folder '+filename
			files.remove(filename)
			shutil.rmtree("/var/www/ekstep/content/"+filename)
	
	
	print files		
	
	#removing the .json files
	for filename in os.listdir("/var/www/ekstep/content/json_files"):
		if filename in files:
			print 'deleted file '+filename
			files.remove(filename)
			os.remove("/var/www/ekstep/content/json_files/"+filename)
