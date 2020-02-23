from django import forms
from user_signup.models import User_Data, User_Diet
from user_signup.models import BUDGET_CHOICES, LAZINESS_CHOICES, DIETARY_CHOICES
from django.forms import ModelForm


class CustomForm(forms.ModelForm):
    class Meta:
        model = User_Data

        fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness', 'dietary_restrictions']

        widgets = {
        'dietary_restrictions': forms.CheckboxSelectMultiple(choices = ['Vegetarian', 'Vegan', 'Peanut']),
        'laziness': forms.Select(choices=LAZINESS_CHOICES),
        'budget': forms.Select(choices=BUDGET_CHOICES)
        }
        #dietary_restrictions = forms.ModelMultipleChoiceField(queryset=User_Diet.objects.all(), required=False)
        #print("MODEL", model.dietary_restrictions)
    def __init__(self, *args, **kwargs):
        # Here kwargs should contain an instance of Supplier
        print("kwargs", kwargs)
        if 'instance' in kwargs:
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data (checked boxes).
            initial['dietary_restrictions'] = [s.pk for s in kwargs['instance'].dietary_restrictions.all()]

        ModelForm.__init__(self, *args, **kwargs)
