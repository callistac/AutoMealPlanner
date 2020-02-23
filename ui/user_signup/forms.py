from django import forms
from user_signup.models import User_Data, User_Diet
from user_signup.models import BUDGET_CHOICES, LAZINESS_CHOICES, DIETARY_CHOICES



class CustomForm(forms.ModelForm):
    class Meta:
        model = User_Data

        fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness', 'dietary_restrictions']

        widgets = {
        'dietary_restrictions': forms.CheckboxSelectMultiple(choices = DIETARY_CHOICES),
        'laziness': forms.Select(choices=LAZINESS_CHOICES),
        'budget': forms.Select(choices=BUDGET_CHOICES)
        }
