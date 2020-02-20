from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class User_Data(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    firstname = models.CharField(max_length=500, default='')
    lastname = models.CharField(max_length=500, default='')
    email = models.EmailField(max_length=500, default='')
    zip = models.IntegerField(default=0)
    budget = models.CharField(max_length=500, default='')
    laziness = models.IntegerField(default=0)
