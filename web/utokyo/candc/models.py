from django.db import models
from django.utils import timezone
# Create your models here.

class Account(models.Model):
    user = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.user}:{self.password}"

def directory_path(instance, filename):
    return  f'{instance.username}/{filename}'

class Puppet(models.Model):
    uid = models.CharField(default='',max_length=30,unique=True)
    username = models.CharField(max_length=30)
    cmd = models.TextField(default='', blank=True)
    upload_file = models.FileField(blank=True, upload_to=directory_path)
    last_access = models.DateTimeField()
    def __str__(self):
        return f"""{self.username} last:{timezone.localtime(self.last_access).strftime("%m/%d %X")}"""
