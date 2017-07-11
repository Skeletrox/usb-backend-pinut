
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

def get_extension(name):
    length = len(name)
    print 'LOOKIN FOR ' + name
    try:
        i = name.index('.')
        return name[i+1:length]
    except ValueError:
        return 'N/A'


class EkFile(models.Model):
    file = models.FileField(upload_to="/var/www/ekstep/")
    slug = models.SlugField(max_length=50, blank=True)
    #link = models.CharField(max_length=500, default='NULL')
    #file_type = models.CharField(max_length=10, default='N/A')

    def __str__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        self.link = os.getcwd()+'file-upload/media/' + self.slug
        self.file_type = get_extension(self.slug)
        print 'EXTENSION IS ' + self.file_type
        print 'SAVED AS ' + self.slug
        #print 'ALSO KNOWN AS ' + self.file
        metadata = FileMetaData(self)
        metadata.save(self)
        super(EkFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        link_name = os.getcwd() + 'file-upload/media/' + self.slug
        #FileMetaData.objects.get(link=link_name).delete()
        self.file.delete(False)
        super(EkFile, self).delete(*args, **kwargs)


class FileMetaData(models.Model):
    file = models.FileField()
    file_type = models.CharField(max_length=10, default="N/A")
    link = models.CharField(max_length=500, primary_key=True)

    def save(self, file_parent, *args, **kwargs):
        self.file = file_parent.file
        self.link = os.getcwd() + 'file-upload/media/' + file_parent.slug
        self.file_type = get_extension(file_parent.slug)
        super(FileMetaData, self).save(*args, **kwargs)