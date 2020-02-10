from django import forms
from django.contrib.auth.models import User

class CustomForm(forms.ModelForm):
    class Meta:
        fields = (
            'email',
        )
