from django import forms
from django.contrib.auth.models import User
from user_signup.models import User_Data_Posts

class CustomForm(forms.ModelForm):
    post = forms.CharField()
    class Meta:
        model = User_Data_Posts
        fields = ('post',)
