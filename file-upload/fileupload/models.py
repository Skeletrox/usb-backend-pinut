
from django.db import models


def get_extension(name):
    length = len(name)
    print 'LOOKIN FOR ' + name
    try:
        i = name.index('.')
        return name[i+1:length]
    except ValueError:
        return 'N/A'


class EkFile(models.Model):
    file = models.FileField(upload_to="pictures")
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
        import os
        self.link = os.getcwd()+'file-upload/media/' + self.slug
        self.file_type = get_extension(self.slug)
        print 'EXTENSION IS ' + self.file_type
        print 'SAVED AS ' + self.slug
        #print 'ALSO KNOWN AS ' + self.file
        super(EkFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(EkFile, self).delete(*args, **kwargs)
