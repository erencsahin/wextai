from django.db import models

class Image(models.Model):
    photographer = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.photographer
