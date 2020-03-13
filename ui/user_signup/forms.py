from django import forms
from user_signup.models import User_Data, User_Diet, Deselect_Options, Rate_Recipes
from user_signup.models import BUDGET_CHOICES, LAZINESS_CHOICES, DIETARY_CHOICES, RATING_CHOICES
from django.forms import ModelForm

class CustomForm(forms.ModelForm):
    '''
    Form that displays users' preferences on the html page
    '''
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
        'dietary_restrictions': forms.CheckboxSelectMultiple(choices = ['Vegetarian', 'Vegan', 'Nuts'
        'Dairy', 'Kosher', 'Gluten free', 'Pescatarian','Halal']),
        'laziness': forms.Select(choices=LAZINESS_CHOICES),
        'budget': forms.Select(choices=BUDGET_CHOICES)
        }

class Deselect(forms.ModelForm):
    '''
    Form that displays users' reasons for deselecting a recipe
    '''
    class Meta:
        model = Deselect_Options
        fields = ['reason']
        labels = {'reason': "Reason for deselecting recipe:"}

class RateRecipe(forms.ModelForm):
    '''
    Form that displays users' ratings of recipes
    '''
    class Meta:
        model = Rate_Recipes
        fields = ['rating']
        labels = {'rating': "What would you rate this recipe on a scale from 1 to 5?"}
