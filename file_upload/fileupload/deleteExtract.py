import shutil,os
def deleteit(name_of_file):
	print 'GOING TO SEND TO THE SHADOW REALM ' + str(name_of_file)
	for filename in os.listdir("/var/www/ekstep/content"):
		folder_to_look_for = name_of_file['folder_file']
		print folder_to_look_for
		if name_of_file['folder_file']==filename:
			print 'deleted file '+filename
			shutil.rmtree("/var/www/ekstep/content/"+filename)
			print 'WE HAVE DESTROYED THE FOLDERS'
		elif name_of_file['json_file']==filename:
			os.remove("/var/www/ekstep/content/"+filename)
			print 'GOODBYE JSON'
