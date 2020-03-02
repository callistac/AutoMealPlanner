from django.urls import reverse
from django.forms import CheckboxSelectMultiple
from multiselectfield import MultiSelectField
from django.db import models

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

DIETARY_CHOICES = [
    ('Vegetarian', 'Vegetarian'),
    ('Vegan', 'Vegan'),
    ('Peanut', 'Peanut')
]

BLACKLIST_CHOICES = [
    ('option1', 'Does not fulfill my dietary restrictions'),
    ('option2', 'Looks gross'),
    ('option3', 'Had a similar meal recently'),
    ('option4', 'Prefer not to answer')
]

# Create your models here.
class User_Diet(models.Model):
    dietary_restrictions = MultiSelectField(choices = DIETARY_CHOICES)

    def __str__(self):
        return self.dietary_restrictions


class User_Data(models.Model):
    firstname = models.CharField(max_length=500, default='')
    lastname = models.CharField(max_length=500, default='')
    email = models.EmailField(max_length=500, default='')
    zip = models.PositiveIntegerField()
    budget = models.CharField(max_length=500, default='', choices = BUDGET_CHOICES)
    laziness = models.CharField(max_length = 50, default = '', choices = LAZINESS_CHOICES)
    dietary_restrictions = models.ManyToManyField(User_Diet, default = "", choices=DIETARY_CHOICES)

    def get_absolute_url(self):
        return reverse('login')


class Deselect_Options(models.Model):
    reason = models.CharField(max_length=500, default='', choices=BLACKLIST_CHOICES)

    def get_absolute_url(self):
        return reverse('/home/dashboard/meals/')
