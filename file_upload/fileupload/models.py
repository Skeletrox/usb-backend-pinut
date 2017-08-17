import os, shutil
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
# Create your models here.


def r_file_name(instance, filename):
    filename = filename.encode('utf-8')
    #print "filename:: " + filename
    #path = settings.CONTENT_ROOT        
    format = filename
    #print "format:: " + format
    return format

content_root = settings.CONTENT_ROOT

class EkFile(models.Model):
    file_upload = models.FileField(upload_to=r_file_name)
    slug = models.SlugField(max_length=50, blank=True)
    type_of_file=models.CharField(max_length=50,blank=True)
    path_of_file=models.CharField(max_length=250,blank=True)

    def __str__(self):
        return self.file_upload.name+","+self.type_of_file+","+self.path_of_file+","+self.slug
       #return file_n+","+self.file_upload.name+","+self.type_of_file+","+self.path_of_file

   
    def save(self, *args, **kwargs):
        self.slug = self.file_upload.name
        index=self.slug.rfind('.')
        self.type_of_file = self.slug[index+1:]
        self.path_of_file = self.file_upload.path
        super(EkFile, self).save(*args, **kwargs)
        shutil.move(content_root+self.file_upload.name,self.path_of_file)
        os.chmod(self.path_of_file, 0644)
        EkFile.objects.filter(file_upload=self.file_upload.name).update(file_upload=self.slug)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file_upload.delete(False)
        super(EkFile, self).delete(*args, **kwargs)
        
        
class Content(models.Model):
        ekfile=models.ForeignKey(EkFile,on_delete=models.CASCADE)
        filename=models.CharField(max_length=250)
        
        def __str__(self):
                return self.filename
                
        def save(self,*args,**kwargs):
                super(Content,self).save(*args,**kwargs)
                
        def delete(self,*args,**kwargs):
                super(Content,self).delete(*args,**kwargs)


class Permission(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	down_to_usb = models.BooleanField(default=False)
	up_from_usb = models.BooleanField(default=False)	
	up_from_dev = models.BooleanField(default=True)
	delete_files = models.BooleanField(default=False)
	ssid_mod = models.BooleanField(default=False)
	captive_mod = models.BooleanField(default=False)
	global_vars_mod = models.BooleanField(default=False)

	def __str__(self):
		return 'Permissions for ' + str(self.user)

	def get_permissions(self):
		perms_dict = {'down_to_usb' : self.down_to_usb,
					  'up_from_usb' : self.up_from_usb,
					  'up_from_dev' : self.up_from_dev,
					  'ssid_mod' : self.ssid_mod,
					  'delete_files' : self.delete_files,
					  'captive_mod' : self.captive_mod,
					  'global_vars_mod' : self.global_vars_mod}
		return perms_dict

@receiver(post_save, sender=User)
def create_permissions (sender, instance, created, **kwargs):
	if created:
		Permission.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_permissions (sender, instance, **kwargs):
	if instance.is_superuser:
		instance.permission.down_to_usb = True
		instance.permission.up_from_usb = True
		instance.permission.up_from_dev = True
		instance.permission.ssid_mod = True
		instance.permission.captive_mod = True
		instance.permission.global_vars_mod = True
		instance.permission.save()
