
from django.db import models


class EkFile(models.Model):
    file = models.FileField(upload_to="pictures")
    slug = models.SlugField(max_length=50, blank=True)

    def __str__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(EkFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(EkFile, self).delete(*args, **kwargs)
