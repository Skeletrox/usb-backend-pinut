import os, inspect 																				#needed for os files
from glob import glob																			#Needed for directories
import subprocess																				#Running lsusb
import getpass																					#used for getuser()
import time																						#temp fix; used to sleep
from stat import *																				#imports stats like ST_SIZE
import threading																				#Multithreading			
from shutil import copy2		 																#Copies files

process = None
staticFileLoc = '/file-upload/media/'
#staticFileLoc = '/Programming/Django/UsbBackend/checkUpdates/static/checkUpdates'				#staticFileLoc for local machine. can be changed based on device
staticFileLocRoot = '/var/www/ekstep/'								#Gives the entire static file root thus is multiuser friendly
count = 0																						#Total number of threads called from main thread, could be useful in determining insertions and deletions?

def check_if_line_usb(line):
	UUID_beg = line.index('UUID') + 5
	UUID_end = line.find('\"', UUID_beg+1)
	if UUID_end - UUID_beg == 10:
		return True
	return False


def transfer_file(file):
	print ('Initiating file transfer')
		#files = [file for file in os.listdir(".") if not os.path.isdir(file)]					#Copies only files as we use a flat filesystem.
		#for file in files:
	sendString = "cp " + file + " " + staticFileLocRoot
	proc = subprocess.Popen (sendString, shell=True )									#Enhanced copy function
	proc.communicate()[0]
	return proc.returncode
	print ('File transfer complete!')
'''
def enableAutoMount():
	fileLines = [ 'KERNEL!="sd[a-z][0-9]", GOTO="media_by_label_auto_mount_end" ',
				  'IMPORT{program}="/sbin/blkid -o udev -p %N" ',
				  'ENV{ID_FS_LABEL}!="", ENV{dir_name}="%E{ID_FS_LABEL}"  ',
				  'ENV{ID_FS_LABEL}=="", ENV{dir_name}="usbhd-%k" ',
				  'ACTION=="add", ENV{mount_options}="relatime"  ',
				  'ACTION=="add", ENV{ID_FS_TYPE}=="vfat|ntfs", ENV{mount_options}="$env{mount_options},utf8,gid=100,umask=002"  ',
				  'ACTION=="add", RUN+="/bin/mkdir -p /media/%E{dir_name}", RUN+="/bin/mount -o $env{mount_options} /dev/%k /media/%E{dir_name}" ',
				  'ACTION=="remove", ENV{dir_name}!="", RUN+="/bin/umount -l /media/%E{dir_name}", RUN+="/bin/rmdir /media/%E{dir_name}"  ',
				  'LABEL="media_by_label_auto_mount_end"']
	f = open('/etc/udev/rules.d/11-media-by-label-auto-mount.rules', 'w')
	for line in fileLines:
		f.write(line+'\n')
	subprocess.Popen("udevadm control --reload-rules", shell=True)
'''
def attemptMount():			
	global count																#Runs when USB is mounted
	os.chdir('/media/' + getpass.getuser())														#Returns the storage location [Should be same across all Linux devices]
	blkid_output = subprocess.check_output("blkid", shell=True)
	blkid_usb_line_list = blkid_output.split("\n")
	blkid_usb_line = blkid_usb_line_list[len(blkid_usb_line_list) - 2]
	print (blkid_usb_line)
	is_usb = check_if_line_usb(blkid_usb_line)
	if not is_usb:
		return None
	label_loc = blkid_usb_line.index("LABEL")
	for i in range(label_loc, len(blkid_usb_line)):
		if blkid_usb_line[i]	 == ' ':
			break
	usb_label = blkid_usb_line[label_loc+7:i-1]
	print (usb_label)
	folders = [name for name in os.listdir(".") if (name == usb_label and os.path.isdir(name))]
	if len(folders) == 0:
		return None	
	currentFolder = folders[0]
	filedict=[]																					#A dictionary of all files
	os.chdir(currentFolder)
	temps = [name for name in os.listdir(".")]
	print 'Temporary files are ' + str(temps)
	files = []
	for root, subfolders, usb_files in os.walk("."):
		for name in usb_files:
			if (not os.path.isdir(name)) and (name[-5:] == '.ecar' or name == 'content.json'):
				files.append(os.path.join(root, name))
	return files

def attemptRemoval():																			#Removes files
	global count
	count += 1
	'''
	byeThread = deleteThread(count)
	byeThread.start()
	'''

def main():
	enableAutoMount()
	df = subprocess.check_output("lsusb", stderr=subprocess.STDOUT)								#suprocess prints to stderr for some reason, making it think stdout is stderr
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
