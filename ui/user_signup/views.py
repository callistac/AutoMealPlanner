from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm, Deselect
from django.views.generic import TemplateView
from django.views import generic
from django.contrib import messages
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.forms import CheckboxSelectMultiple
from django import forms
from django.http import Http404
import sqlite3
from user_signup.models import User_Data, User_Diet, Deselect_Options
from bootstrap_modal_forms.generic import BSModalCreateView
from user_signup.generate_recipes import generate_html_page

def user_signup(request):
    return render(request, 'user_signup/user_signup.html', {})

def home(request):
    return render(request, 'user_signup/home.html', {})

def new_user(request):
    return render(request, 'user_signup/new_user.html', {})

def about(request):
    return render(request, 'user_signup/about.html', {})

class User_Info(TemplateView):
    template_name = 'user_signup/user_data_form.html'

    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        user_data_statement = "INSERT INTO user_signup_user_data (firstname, lastname, email, zip, budget, laziness) VALUES (?, ?, ?, ?, ?, ?)"
        diet_statement = "INSERT INTO user_diet (dietary_restrictions, user_id) VALUES (?, ?)"
        select_user_unique_id = "SELECT id FROM user_signup_user_data ORDER BY id DESC LIMIT 1"
        connection = sqlite3.connect('db.sqlite3')

        results = []
        diets = []
        for key, value in request.POST.lists():
            if key == 'dietary_restrictions':
                diets.append(value)
            else:
                results.append(value[0])

        c = connection.cursor()
        c.execute(user_data_statement, results[1:])
        c.execute(select_user_unique_id)
        unique_id = c.fetchone()

        for diet in diets[0]:
            c.execute(diet_statement, (diet, unique_id[0]))

        connection.commit()
        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have signed up successfully, log in to get started!')
        return redirect("/home/login")
'''
class MealGeneration(TemplateView):
    def get(self, request):
        print("HEY")
        args = {'user': request.user}
        generate_html_page()
        return render(request, 'user_signup/meals.html', args)

    def post(self, request):
        return redirect("/home/dashboard/meals.html")
'''
class MealGeneration(TemplateView):
    def get(self, request):
        print("HEY")
        form = Deselect()
        args = {'user': request.user, 'form':form}
        generate_html_page()
        return render(request, 'user_signup/meals.html', args)

    def post(self, request):
        print("IN POST REQUST")
        print(request.POST)
        return redirect("/home/dashboard/meals/")

class Change_User_Info(TemplateView):
    template_name = 'user_signup/user_preferences.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        update_info_statement = ""
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')

class BlackListView(TemplateView):
    template_name = "user_signup/meals.html"
    def get(self, request):
        print("HELLO")
        form = Deselect()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        print("IN POST REQUST")
        print(request.POST)
        return redirect("/home/dashboard/meals/")

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
            messages.add_message(request, messages.SUCCESS, 'Input is invalid!')
            args = {'form':form}
            return render(request, 'user_signup/new_user.html', args)
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
