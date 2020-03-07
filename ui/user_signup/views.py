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

        # if the user has filled out the dietary restrictions form, truth=True
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

        if len(diets)>0:
            for diet in diets[0]:
                c.execute(diet_statement, (diet, request.user.id))
        else:
            c.execute(diet_statement, ("N/A", request.user.id))


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

        if len(user_info) == 0:
            user_info = ['']
        args = {'user': request.user, 'form':form, 'name':user_info[1]}

        # recipes = query_recipes()
        # check to see if the recipes we extracted fufill user's budget
        # check to see if the recipes we extracted are not in the blacklisted recipes for that user
        # if not, regenerate recipes
        connection.commit()
        connection.close()
        recipes = [(10, 'Pork Dumplings', 'https://www.allrecipes.com/recipe/14759/pork-dumplings/', 'https://images.media-allrecipes.com/userphotos/560x315/704866.jpg'),
                    (27, 'Easy Lemon-Pepper Blackened Salmon', 'https://www.allrecipes.com/recipe/156814/easy-lemon-pepper-blackened-salmon/', 'https://images.media-allrecipes.com/userphotos/560x315/7249818.jpg')]
        ingredients = ['apples', 'tomatoes', 'lunchmeat', 'pizza']

        request.session['recipes'] = recipes
        request.session['ingredients'] = ingredients

        filename = 'meals.html'
        generate_html_page(filename, recipes)
        return render(request, 'user_signup/'+filename, args)

    def post(self, request):
        print(request.user)
        #insert_blacklist_statement = "INSERT INTO blacklisted_recipes (recipe_id, user_id, reason) VALUES (?, ?, ?)"
        insert_blacklist_statement = "UPDATE blacklisted_recipes SET reason = '%s' WHERE ID = (SELECT MAX(ID) FROM blacklisted_recipes)"%(request.POST['reason'])
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        results = []
        results.append("999999999999999")
        results.append(request.user.id)
        results.append(request.POST['reason'])
        print(results)
        #c = c.execute(insert_blacklist_statement, )
        generate_html_page('meals.html', request.session['recipes'])
        return redirect("/home/dashboard/meals/")

def SaveRecipes(request):
    if request.method == "POST":
        # generating text file with ingredients
        with open('grocery_list.txt', 'w') as f:
            for item in request.session.get('ingredients'):
                f.write("%s\n" % item)

        # save the recipes to the database
        recipes = request.session.get('recipes')
        insert_into_user_recipes_state = "INSERT INTO user_recipes_rating (recipe_id, user_id, rating, week) VALUES (?, ?, ?, ?)"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        prev_week_state = 'SELECT week FROM user_recipes_rating WHERE user_id = ? ORDER BY week DESC'
        c.execute(prev_week_state, (request.user.id,))
        last_week = c.fetchone()

        if last_week is None:
            current_week = 0
        else:
            current_week = last_week[0] + 1
        for recipe in recipes:
            c.execute(insert_into_user_recipes_state, (recipe[0], request.user.id, None, current_week))

        connection.commit()
        connection.close()
        return redirect("/home/dashboard")

class DisplayPastRecipes(TemplateView):
    def get(self, request):
        form = Deselect()
        sql_statement = "SELECT * FROM user_signup_user_data WHERE user_id = ?"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c.execute(sql_statement, (request.user.id,))
        user_info = c.fetchone()

        if len(user_info) == 0:
            user_info = ['']
        args = {'user': request.user, 'form':form, 'name':user_info[1]}
        prev_week_state = 'SELECT * FROM user_recipes_rating WHERE user_id = ? ORDER BY week DESC LIMIT 7'

        c.execute(prev_week_state, (request.user.id,))
        past_recipes = c.fetchall()
        print(past_recipes)

        connection.commit()
        connection.close()

        filename = 'past_meals.html'
        generate_html_page(filename, past_recipes)
        return render(request, 'user_signup/'+filename, args)



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
        #NEED TO CHANGE NAME TO RECIPE.ID WHEN CORRECT TABLE IS DONE
        print("USER", request.user)
        name = request.GET.get('name')
        print("NAME", type(name))

        insert_blacklist_statement = "INSERT INTO blacklisted_recipes (recipe_id, user_id, reason) VALUES (?, ?, ?)"

        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_blacklist_statement, (name, request.user.id, "Nothing"))
        connection.commit()
        #c.close()
        #connection.close()

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
