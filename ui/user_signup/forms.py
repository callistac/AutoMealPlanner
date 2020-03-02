from django import forms
from user_signup.models import User_Data, User_Diet, Deselect_Options
from user_signup.models import BUDGET_CHOICES, LAZINESS_CHOICES, DIETARY_CHOICES


class CustomForm(forms.ModelForm):
    class Meta:
        model = User_Data

        fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness', 'dietary_restrictions']

        labels = {
            'firstname': "First name",
            'lastname': "Last name",
            'email': 'Email Address',
            'zip': "Zip code",
            'budget': "Weekly Budget",
            'laziness': "Effort",
            'dietary_restrictions': "Dietary Restrictions (select all that apply)"
        }

        widgets = {
        'dietary_restrictions': forms.CheckboxSelectMultiple(choices = DIETARY_CHOICES),
        'laziness': forms.Select(choices=LAZINESS_CHOICES),
        'budget': forms.Select(choices=BUDGET_CHOICES)
        }

class Deselect(forms.ModelForm):
    class Meta:
        model = Deselect_Options
        fields = ['reason']
        labels = {'reason': "Reason for deselecting recipe:"}
