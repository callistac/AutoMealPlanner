from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm, Deselect
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from user_signup.query_recipes import query_recipes
from django.http import HttpResponse
import sqlite3
import numpy as np


def home(request):
    return render(request, 'user_signup/home.html', {})

def about(request):
    return render(request, 'user_signup/about.html', {})

def about_redirect(request):
    return redirect('/home/about')

class User_Dashboard(TemplateView):
    template_name = 'user_signup/dashboard.html'

    def get(self, request):
        form = CustomForm()
        sql_statement = "SELECT firstname FROM user_signup_user_data WHERE user_id = ?"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c.execute(sql_statement, (request.user.id,))
        name = c.fetchone()

        if name is not None:
            truth = True
        else:
            name = ['']
            truth = False

        args = {'user_complete':truth, 'form':form, 'name':name[0]}
        return render(request, 'user_signup/dashboard.html', args)

    def post(self, request):
        user_data_statement = "INSERT INTO user_signup_user_data (user_id, firstname, lastname, email, zip, budget, laziness) VALUES (?, ?, ?, ?, ?, ?, ?)"
        diet_statement = "INSERT INTO user_diet (dietary_restrictions, user_id) VALUES (?, ?)"
        select_user_unique_id = "SELECT id FROM user_signup_user_data ORDER BY id DESC LIMIT 1"
        connection = sqlite3.connect('db.sqlite3')

        results = []
        diets = []
        results.append(request.user.id)
        for key, value in request.POST.lists():
            if key == 'csrfmiddlewaretoken':
                pass
            elif key == 'dietary_restrictions':
                diets.append(value)
            else:
                results.append(value[0])

        c = connection.cursor()
        c.execute(user_data_statement, results)

        for diet in diets[0]:
            c.execute(diet_statement, (diet, request.user.id))

        connection.commit()
        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have finished with the creation of your account.')
        return redirect("/home/dashboard")


class MealGeneration(TemplateView):
    def get(self, request):
        form = Deselect()
        sql_statement = "SELECT * FROM user_signup_user_data WHERE user_id = ?"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c.execute(sql_statement, (request.user.id,))
        user_info = c.fetchone()
        print(user_info)

        if len(user_info) == 0:
            user_info = ['']
        args = {'user': request.user, 'form':form, 'name':user_info[1]}

        # recipes = query_recipes()
        # check to see if the recipes we extracted fufill user's budget
        # check to see if the recipes we extracted are not in the blacklisted recipes for that user
        # if not, regenerate recipes
        connection.commit()
        connection.close()
        recipes = [('Pork Dumplings', 'https://www.allrecipes.com/recipe/14759/pork-dumplings/', 'https://images.media-allrecipes.com/userphotos/560x315/704866.jpg'),
                    ('Easy Lemon-Pepper Blackened Salmon', 'https://www.allrecipes.com/recipe/156814/easy-lemon-pepper-blackened-salmon/', 'https://images.media-allrecipes.com/userphotos/560x315/7249818.jpg')]
        ingredients = ['apples', 'tomatoes', 'lunchmeat', 'pizza']

        request.session['recipes'] = recipes
        request.session['ingredients'] = ingredients

        generate_html_page(recipes)
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
        generate_html_page()
        return redirect("/home/dashboard/meals/")

# is only called when the generate ingredients recipe is called so we have our final recipes
def SaveRecipes(request):
    if request.method == "POST":
        print(request.user.id)
        print(request.session.get('recipes'))
        print(request.session.get('ingredients'))

        with open('grocery_list.txt', 'w') as f:
            for item in request.session.get('ingredients'):
                f.write("%s\n" % item)
        # save the recipes to the database
        return redirect("/home/dashboard")

class Change_User_Info(TemplateView):
    template_name = 'user_signup/user_preferences.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        update_info_statement = ""
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')

class Deselect_Tracker(TemplateView):
    def get(self, request):
        print("USER", request.user)
        name = request.GET.get('name')
        print("NAME", name)
        # NEED TO STORE RECIPE NAME SOMEWHERE
        #return render(request, self.template_name, {'form':form})
    def post(self, request):
        return


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/home/login/")
        else:
            form = UserCreationForm()
            messages.add_message(request, messages.SUCCESS, 'Input is invalid!')
            args = {'form':form}
            return render(request, 'user_signup/new_user.html', args)
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)
