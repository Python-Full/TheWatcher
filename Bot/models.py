from django.db import models


# Create your models here.
class Site(models.Model):
    url = models.URLField(unique=True)
    state = models.BooleanField(default=False)


class Client(models.Model):
    chat_id = models.CharField(max_length=199, unique=True)
    chat_name = models.CharField(max_length=199, )
    username = models.CharField(max_length=199, null=True)
    lastname = models.CharField(max_length=199, null=True)
    url = models.ManyToManyField(Site, related_name='urls', blank=True)
    counter = models.IntegerField(default=1)
