from django import forms
#from django.contrib.auth.models import User
from user_signup.models import User_Data, User_Diet

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
('blah', 'blah')
]


class CustomForm(forms.ModelForm):
    class Meta:
        model = User_Data

        #dietary_restrictions = forms.MultipleChoiceField(required=False, choices = DIETARY_CHOICES)
        fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness', 'dietary_restrictions']

        widgets = {
        'dietary_restrictions': forms.CheckboxSelectMultiple(choices=DIETARY_CHOICES),
        'laziness': forms.Select(choices=LAZINESS_CHOICES),
        'budget': forms.Select(choices=BUDGET_CHOICES)
        }

        '''
        firstname = forms.CharField(max_length=500)
        lastname = forms.CharField(max_length=500)
        email = forms.EmailField(max_length=500)
        zip = forms.IntegerField()
        budget = forms.CharField(
                max_length=500,
                widget=forms.Select(choices=BUDGET_CHOICES),
            )
        laziness = forms.CharField(
                max_length=50,
                widget=forms.Select(choices=LAZINESS_CHOICES),
            )
        print(User_Diet.objects.all())
        dietary_restrictions = forms.ModelMultipleChoiceField(queryset=User_Data.objects.all(),
            widget=forms.CheckboxSelectMultiple(),
            required=False)

        dietary_restrictions = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(),
                                         choices=DIETARY_CHOICES)
        '''
        #exclude = []
