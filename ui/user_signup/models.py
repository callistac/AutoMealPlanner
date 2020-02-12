from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class User_Data_Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    post = models.CharField(max_length=500, default='')
