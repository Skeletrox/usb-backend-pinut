
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .extract import extractit
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
    file = models.FileField(upload_to="")
    slug = models.SlugField(max_length=50, blank=True)
    link = models.CharField(max_length=500, default='NULL', blank=True)
    file_type = models.CharField(max_length=10, default='N/A', blank=True)

    def __str__(self):
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        self.link = '/var/www/ekstep/' + self.slug
        self.file_type = get_extension(self.slug)
        print 'EXTENSION IS ' + self.file_type
        print 'SAVED AS ' + self.slug
	print 'HAVING LINK ' + self.link
        #print 'ALSO KNOWN AS ' + self.file
        super(EkFile, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        link_name = os.getcwd() + 'file-upload/media/' + self.slug
        #FileMetaData.objects.get(link=link_name).delete()
        self.file.delete(False)
        super(EkFile, self).delete(*args, **kwargs)



