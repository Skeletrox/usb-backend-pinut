import os, inspect, json 																				#needed for os files
from django.conf import settings
from glob import glob																			#Needed for directories
import subprocess																				#Running lsusb
import getpass																					#used for getuser()
import time																						#temp fix; used to sleep
from stat import *																				#imports stats like ST_SIZE
import threading																				#Multithreading			
from shutil import copy2		 																#Copies files

process = None
<<<<<<< HEAD

config_file = settings.CONFIG_FILE
with open(config_file) as res_file:
=======
with open('/support_files/res.json') as res_file:
>>>>>>> refs/remotes/origin/master
	try:
		json_data = json.load(res_file)
                active_profile = json_data["active_profile"]
                staticFileLocRoot = json_data[active_profile].get("media_root", "")
                #print "staticFileLocRoot " + staticFileLocRoot
		#staticFileLocRoot = json_data["global_vars"].get("media_root", "")
	except:
		staticFileLocRoot = '/'

def get_usb_name():
	lsblk_out = subprocess.check_output("lsblk", shell=True)
	lsblk_list = lsblk_out.split('\n')
	media_dir = None
	for line in lsblk_list:
		if '/media/' in line:
			media_loc = line.index('/media/')
			media_dir = line[media_loc:].strip()
	return media_dir

def check_if_line_usb(line):
	UUID_beg = line.index('UUID') + 5
	UUID_end = line.find('\"', UUID_beg+1)
	print str(UUID_end - UUID_beg)
	if UUID_end - UUID_beg == 10:
		return True
	return False

def transfer_file(file):
	sendString = "cp " + file + " " + staticFileLocRoot + file
	proc = subprocess.Popen (sendString, shell=True)									
	proc.communicate()[0]
	return proc.returncode

def attemptMount():		
	lsblk_out = subprocess.check_output("lsblk", shell=True)
	lsblk_list = lsblk_out.split('\n')
	media_dir = None
	for line in lsblk_list:
		if '/media/' in line:
			media_loc = line.index('/media/')
			media_dir = line[media_loc:].strip()
	if media_dir is None:
		return None
	os.chdir(media_dir)
	temps = [name for name in os.listdir(".")]
	print 'Temporary files are ' + str(temps)
	files = []
	for root, subfolders, usb_files in os.walk("."):
		for name in usb_files:
			if (not os.path.isdir(name)) and (name[-5:] == '.ecar' or name == 'content.json'):
				files.append(os.path.join(root, name))
	return files

def main():
	#enableAutoMount()
	df = subprocess.check_output("lsusb", stderr=subprocess.STDOUT)								#subprocess prints to stderr for some reason, making it think stdout is stderr
	oldDeviceList = df.split("\n")																#gets list of previously connected usb devices
	while True:
		df = subprocess.check_output("lsusb", stderr=subprocess.STDOUT)							#do it again
		newDeviceList = df.split('\n')															#store in a NEW list

		if len(newDeviceList) > len(oldDeviceList):												#new usb device inserted!
			for line in newDeviceList:
				if line not in oldDeviceList:													#this points to the newer device we have attached
					IDAnchor = line.index("ID")														
					line = line[IDAnchor:]														#slice off unwanted line info [such as bus information]
					print ("You have attached " + line)											#debug purposes	
					time.sleep(3)																#prevents python from attempting to access the files before the OS itself, might need to be increased 
					attemptMount()																#attempt mounting the device	

		if len(newDeviceList) < len(oldDeviceList):												#some USB device has been removed!
			for line in oldDeviceList:
				if line not in newDeviceList:
					IDAnchor = line.index("ID")
					line = line[IDAnchor:]
					print ("You have removed " + line)
					attemptRemoval()
		oldDeviceList = list(newDeviceList)														#allows for the loop to function properly

if __name__ == '__main__':
	main()
