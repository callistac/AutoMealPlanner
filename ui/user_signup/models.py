from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse


# Create your models here.
class User_Data(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    BUDGET_CHOICES = [
        ('<$40', '<$40'),
        ('$40-60', '$40-60'),
        ('$60-80', '$60-80'),
        ('$80-100', '$80-100'),
        ('>$100', '>$100')
    ]

    LAZINESS_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3','3'),
    ('4', '4'),
    ('5','5')
    ]

    firstname = models.CharField(max_length=500, default='')
    lastname = models.CharField(max_length=500, default='')
    email = models.EmailField(max_length=500, default='')
    zip = models.PositiveIntegerField()
    budget = models.CharField(max_length=500, default='', choices = BUDGET_CHOICES)
    laziness = models.CharField(max_length = 50, choices = LAZINESS_CHOICES)

    def get_absolute_url(self):
        #return HttpResponseRedirect(reverse('login'))
        return reverse('login')
