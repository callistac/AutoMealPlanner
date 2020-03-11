from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm, Deselect, RateRecipe
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from user_signup.query_recipes import query_recipes
from django.http import HttpResponse
import sqlite3
import numpy as np
from django.http import FileResponse



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

        try:
            query_blacklist = "SELECT recipe_num FROM blacklisted_recipes WHERE ID = (SELECT MAX(ID) FROM blacklisted_recipes)"
            c.execute(query_blacklist)
            black_id = c.fetchone()[0]
            recipes, ingredients = query_recipes(user_info, blacklist = [black_id], past_recipes = request.session['recipes'], past_ingredients = request.session['ingredients'])
        except:
            recipes, ingredients = query_recipes(user_info, blacklist = [], past_recipes = None, past_ingredients = None)

        request.session['recipes'] = recipes
        request.session['ingredients'] = ingredients
        filename = 'meals.html'
        connection.commit()
        connection.close()
        generate_html_page(filename, recipes)
        return render(request, 'user_signup/'+filename, args)

    def post(self, request):
        insert_blacklist_statement = "UPDATE blacklisted_recipes SET reason = '%s' WHERE ID = (SELECT MAX(ID) FROM blacklisted_recipes)"%(request.POST['reason'])
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        sql_statement = "SELECT * FROM user_signup_user_data WHERE user_id = ?"
        c.execute(sql_statement, (request.user.id,))
        user_info = c.fetchone()
        c = c.execute(insert_blacklist_statement )
        connection.commit()

        generate_html_page('meals.html', request.session['recipes'])
        return redirect("/home/dashboard/meals/")

class Deselect_Tracker(TemplateView):
    def get(self, request):
        recipe_id = request.GET.get('name')
        print("NAME", (recipe_id))
        insert_blacklist_statement = "INSERT INTO blacklisted_recipes (recipe_num, user_id, reason) VALUES (?, ?, ?)"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_blacklist_statement, (recipe_id, request.user.id, "Nothing"))
        connection.commit()

class Rating(TemplateView):
    def get(self, request):
        recipe_id = request.GET.get('name')
        request.session['recipe_number'] = recipe_id
        insert_rating = "INSERT INTO rated_recipes (recipe_num, user_id) VALUES (?,?)"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_rating, (recipe_id, request.user.id))
        connection.commit()


def DownloadFile(request):
    recipes = request.session.get('recipes')
    insert_into_user_recipes_state = "INSERT INTO user_past_recipes (recipe_id, user_id, week) VALUES (?, ?, ?)"
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
    prev_week_state = 'SELECT week FROM user_past_recipes WHERE user_id = ? ORDER BY week DESC'
    c.execute(prev_week_state, (request.user.id,))
    last_week = c.fetchone()

    if last_week is None:
        current_week = 0
    else:
        current_week = last_week[0] + 1
    for recipe in recipes:
        c.execute(insert_into_user_recipes_state, (recipe[0], request.user.id, current_week))

    connection.commit()
    connection.close()
    # generating text file with ingredients
    filename = 'grocery_list.txt'
    with open(filename, 'w') as f:
        for item in request.session.get('ingredients'):
            f.write("%s\n" % item[1])

    response = FileResponse(open(filename, 'rb'), as_attachment = True)
    response['Content-Type']='text/html'
    response['Content-Disposition'] = "attachment; filename=%s"%(filename)
    return response


class DisplayPastRecipes(TemplateView):
    def get(self, request):
        form = RateRecipe()
        recipe_id = request.GET.get('name')
        request.session['recipe_num'] = recipe_id
        sql_statement = "SELECT * FROM user_signup_user_data WHERE user_id = ?"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c.execute(sql_statement, (request.user.id,))
        user_info = c.fetchone()

        if len(user_info) == 0:
            user_info = ['']
        args = {'user': request.user, 'form':form, 'name':user_info[1]}
        prev_week_state = 'SELECT recipe_id FROM user_past_recipes WHERE user_id = ? ORDER BY week DESC LIMIT 7'

        c.execute(prev_week_state, (request.user.id,))
        past_recipes = c.fetchall()

        sql_recipes = "SELECT * FROM recipes WHERE recipe_num = ?"
        previous_recipes = []
        for recipe in past_recipes:
            c.execute(sql_recipes, (recipe[0], ))
            prev_recipe = c.fetchone()
            previous_recipes.append(prev_recipe)

        connection.commit()
        connection.close()

        filename = 'past_meals.html'
        generate_html_page(filename, previous_recipes)
        return render(request, 'user_signup/'+filename, args)

    def post(self, request):
        insert_rating_statement = "UPDATE rated_recipes SET rating = '%d' WHERE id = (SELECT MAX(id) FROM rated_recipes)"%(int(request.POST['rating'][-1]),)
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_rating_statement)
        connection.commit()
        connection.close()
        return redirect("/home/dashboard/past_recipes/")

class Change_User_Info(TemplateView):
    template_name = 'user_signup/user_preferences.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()

        for key, value in request.POST.lists():
            print(key)
            print(value)
            if key == 'csrfmiddlewaretoken':
                pass
            else:
                if key == 'firstname':
                    field = 'firstname'
                elif key == 'lastname':
                    field = 'lastname'
                elif key == 'email':
                    field = 'email'
                elif key == 'zip':
                    field = 'zip'
                elif key == 'budget':
                    field = 'budget'
                elif key == 'laziness':
                    field = 'laziness'
                elif key == 'dietary_restrictions':
                    field = 'dietary_restrictions'

                update_statement = "UPDATE user_signup_user_data SET " + field + " = '%s' WHERE user_id = '%s'"%(value[0], request.user.id)
                c = c.execute(update_statement)
                connection.commit()

        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')
        return redirect("/home/dashboard")

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
