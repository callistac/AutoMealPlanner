from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm, Deselect
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
import sqlite3


def home(request):
    return render(request, 'user_signup/home.html', {})

def about(request):
    return render(request, 'user_signup/about.html', {})

def about_redirect(request):
    return redirect('/home/about')

def profile(request):
    args = {'user': request.user}
    return render(request, 'user_signup/dashboard.html', args)

class User_Info(TemplateView):
    template_name = 'user_signup/user_data_form.html'

    def get(self, request):
        form = CustomForm()
        print(request.user)
        args = {'user': request.user, 'form':form}
        return render(request, self.template_name, args)

    def post(self, request):
        # selecting last signed up user from auth_user
        #auth_user_statement = "SELECT id FROM auth_user ORDER BY id DESC LIMIT 1"
        user_data_statement = "INSERT INTO user_signup_user_data (firstname, lastname, email, zip, budget, laziness) VALUES (?, ?, ?, ?, ?, ?)"
        diet_statement = "INSERT INTO user_diet (dietary_restrictions, user_id) VALUES (?, ?)"
        select_user_unique_id = "SELECT id FROM user_signup_user_data ORDER BY id DESC LIMIT 1"
        connection = sqlite3.connect('db.sqlite3')

        results = []
        diets = []
        #c.execute(auth_user_statement)
        #auth_user_id = c.fetchone()
        #results.append(auth_user_id)
        for key, value in request.POST.lists():
            if key == 'csrfmiddlewaretoken':
                pass
            elif key == 'dietary_restrictions':
                diets.append(value)
            else:
                results.append(value[0])

        print(results)
        c = connection.cursor()
        c.execute(user_data_statement, results)
        c.execute(select_user_unique_id)
        unique_id = c.fetchone()

        for diet in diets[0]:
            c.execute(diet_statement, (diet, unique_id[0]))

        connection.commit()
        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have signed up successfully, log in to get started!')
        return redirect("/home/login")

class MealGeneration(TemplateView):
    def get(self, request):
        form = Deselect()
        args = {'user': request.user, 'form':form}
        generate_html_page()
        return render(request, 'user_signup/meals.html', args)

    def post(self, request):
        print(request.user)
        insert_blacklist_statement = "INSERT INTO blacklisted_recipes (recipe_id, user_id, reason) VALUES (?, ?, ?)"
        connection = sqlite3.connect('db.sqlite3')

        results = []
        results.append(request.user.id)
        results.append(request.POST['reason'])

        print(results)
        #c = c.execute(insert_blacklist_statement, )
        return redirect("/home/dashboard/meals/")

class Change_User_Info(TemplateView):
    template_name = 'user_signup/user_preferences.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        update_info_statement = ""
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')


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
