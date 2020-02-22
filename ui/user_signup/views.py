from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm
from django.views.generic import TemplateView
from django.contrib import messages
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.forms import CheckboxSelectMultiple
from django import forms
from django.http import Http404
# Create your views here.
from user_signup.models import User_Data, User_Diet

def user_signup(request):
    return render(request, 'user_signup/user_signup.html', {})

def home(request):
    return render(request, 'user_signup/home.html', {})

def new_user(request):
    return render(request, 'user_signup/new_user.html', {})

def about(request):
    return render(request, 'user_signup/about.html', {})

def user_info(request):
    if request.method == 'POST':
        print(request.POST.getlist('firstname'))
        form = CustomForm(request.POST)
        messages.add_message(request, messages.SUCCESS, 'You have signed up successfully!')
        return redirect("/home/login")
    else:
        form = UserCreationForm()
        args = {"form":form}

        return render(request, 'user_signup/user_information.html', args)

class User_Entry(CreateView):
    model = User_Data
    fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness', 'dietary_restrictions']
    widgets = {'dietary_restrictions': CheckboxSelectMultiple}

class User_Update(UpdateView):
    model = User_Data
    fields = ['firstname', 'lastname', 'email', 'zip', 'budget', 'laziness']
    manyfields = ['dietary_restrictions']


class User_Info(TemplateView):
    #template_name = 'user_signup/user_information.html'
    template_name = 'user_signup/user_data_form.html'

    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        print(request.POST)
        form = CustomForm(request.POST)
        print(form.fields['dietary_restrictions'].choices)
        #print(form)
        print(form.errors)
        if form.is_valid():
            print("HELLO")
            post = form.save(commit = False)
            print(post)
            post.user = request.user
            print(post.user)
            post.save()
            # post below comes from initalization in forms.py
            text = form.cleaned_data['firstname']
            form = CustomForm()
            return redirect('/home/dashboard')

        args = {'form':form}
        return render(request, self.template_name, args)

def about_redirect(request):
    return redirect('/home/about')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/home/login/new_user/user_info")
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)

def profile(request):
    args = {'user': request.user}
    return render(request, 'user_signup/dashboard.html', args)

def user_preferences(request):
    if request.method == 'POST':
        print(request.POST.getlist('firstname'))
        form = CustomForm(request.POST)
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')
        return redirect("/home/dashboard")
    else:
        form = UserCreationForm()
        args = {"form":form}

        return render(request, 'user_signup/user_preferences.html', args)
