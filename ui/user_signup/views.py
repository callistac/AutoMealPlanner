from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user_signup.forms import CustomForm, Deselect, RateRecipe
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from user_signup.query_recipes import query_recipes
from django.http import HttpResponse
from django.http import FileResponse
import sqlite3
import numpy as np
import user_signup.make_grocery_list as mgl

def home(request):
    '''
    Displays home page
    '''
    return render(request, 'user_signup/home.html', {})

def about(request):
    '''
    Displays about page
    '''
    return render(request, 'user_signup/about.html', {})

def about_redirect(request):
    '''
    Redirects to about page from home page
    '''
    return redirect('/home/about')

class User_Dashboard(TemplateView):
    '''
    Displays the user's dashboard (either the generate new weekly menu button or
    the form that asks for user's name, budget, etc.)

    GET request -> generates custom form from forms.py to record user's name,
    budget, dietary restrictions, etc.

    POST request -> inserts data from custom form into two SQL tables,
    one which stores dietary restrictions and another that stores all other information
    '''
    template_name = 'user_signup/dashboard.html'

    def get(self, request):
        form = CustomForm()
        sql_statement = "SELECT firstname FROM user_signup_user_data WHERE user_id = ?"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c.execute(sql_statement, (request.user.id,))
        name = c.fetchone()

        # if the user has filled out the custom form already, truth=True
        if name is not None:
            truth = True
        else:
            name = ['']
            truth = False

        args = {'user_complete':truth, 'form':form, 'name':name[0]}
        return render(request, 'user_signup/dashboard.html', args)

    def post(self, request):
        user_data_statement = "INSERT INTO user_signup_user_data (user_id, firstname, lastname, email, zip, budget, laziness)\
                                VALUES (?, ?, ?, ?, ?, ?, ?)"
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

        if len(diets)> 0:
            for diet in diets[0]:
                c.execute(diet_statement, (diet, request.user.id))

        connection.commit()
        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have finished with the creation of your account.')
        return redirect("/home/dashboard")


class MealGeneration(TemplateView):
    '''
    Generates the randomly selected weekly meals webpage

    GET request -> loads weekly meals webpage by randomly selecting recipes using the query_recipes
                    function and generates the webpage by calling the generate_html_page function.
                    Also, loads in the Deselect() form which prompts a user to describe why they
                    are deselecting a given recipe

    POST request -> stores the user's information for why they are deselecting a recipe and regenerates
                    the users meal page, pulling a new recipe for the recipe they deselected
    '''
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
            recipes, ingredients = \
                query_recipes(user_info, blacklist = [black_id],\
                    past_recipes = request.session['recipes'], past_ingredients = request.session['ingredients'])
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
        insert_blacklist_statement = "UPDATE blacklisted_recipes SET reason = '%s' WHERE ID = (SELECT MAX(ID)\
                                    FROM blacklisted_recipes)"%(request.POST['reason'])
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
    '''
    Keeps track of which recipe the user deselected in the meals.html page by inserting
    the recipe number, user id, and their reasoning (we insert this as a placeholder but
    actually input their reason in the POST request of MealGeneration view)
    '''
    def get(self, request):
        recipe_id = request.GET.get('name')
        insert_blacklist_statement = "INSERT INTO blacklisted_recipes (recipe_num, user_id, reason) VALUES (?, ?, ?)"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_blacklist_statement, (recipe_id, request.user.id, "Nothing"))
        connection.commit()

class Rating(TemplateView):
    '''
    Keeps track of the rating a user gives a past recipe and inserts that Rating into
    the rated_recipes table along with the user's ID
    '''
    def get(self, request):
        recipe_id = request.GET.get('name')
        request.session['recipe_number'] = recipe_id
        insert_rating = "INSERT INTO rated_recipes (recipe_num, user_id) VALUES (?,?)"
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_rating, (recipe_id, request.user.id))
        connection.commit()

def DownloadFile(request):
    '''
    Downloads the weekly ingredients to a text file and stores this weekly menu into the
    user_past_recipes table so that a user can have access to last week's meals
    '''
    recipes = request.session.get('recipes')
    insert_into_user_recipes_state = "INSERT INTO user_past_recipes (recipe_id, user_id, week) VALUES (?, ?, ?)"
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
    # finds the last week (digit, starting with 0) that a user generated meals
    prev_week_state = 'SELECT week FROM user_past_recipes WHERE user_id = ? ORDER BY week DESC'
    c.execute(prev_week_state, (request.user.id,))
    last_week = c.fetchone()

    # if this is the users first week ever generating a meal, current_week = 0
    # if it is not the users first time, sets their current_week = last_week + 1
    if last_week is None:
        current_week = 0
    else:
        current_week = last_week[0] + 1
    for recipe in recipes:
        c.execute(insert_into_user_recipes_state, (recipe[0], request.user.id, current_week))

    # finds the recipe info we need to generate an estimated weekly price using make_grocery_list and
    # estimated_grocery_price functions
    recip_ids = tuple([x[0] for x in recipes])
    grocery_list = "SELECT recipes.servings, recipe_ingred.amount, recipe_ingred.unit,  \
    ingred_codes.name, recipes.title FROM recipe_ingred JOIN recipes JOIN ingred_codes ON\
    recipe_ingred.recipe_num = recipes.recipe_num AND recipe_ingred.ingredient_id = ingred_codes.ingredient_id\
    WHERE recipes.recipe_num IN {}".format(recip_ids)
    c.execute(grocery_list)
    ingreds = c.fetchall()
    grocery_ingreds = mgl.make_grocery_list(ingreds)
    prices = mgl.estimate_grocery_price(grocery_ingreds)

    # writes/saves ingredients and price to a text file
    recipes = []
    filename = 'grocery_list.txt'
    with open(filename, 'w') as f:
        for item in ingreds:
            recipe = item[4]
            if recipe not in recipes:
                f.write('\n')
                recipes.append(recipe)
                f.write("***%s***\n" % item[4])
                f.write("%s\n" % item[3])
            else:
                f.write("%s\n" % item[3])

        f.write('\n')
        f.write("Your raw price per serving is $%s \nYour total estimated price is $%s" %(prices[0], prices[1]))

    response = FileResponse(open(filename, 'rb'), as_attachment = True)
    response['Content-Type']='text/html'
    response['Content-Disposition'] = "attachment; filename=%s"%(filename)
    connection.commit()
    connection.close()
    return response

class DisplayPastRecipes(TemplateView):
    '''
    Similar view to MealGeneration but includes an option for a user to rate a past
    recipe instead of having the ability to deselect, loads in RateRecipe form

    GET request -> loads in RateRecipe form and queries last weeks recipe (assuming
    the user generated 7 recipes last week), displays these past recipes by calling
    generate_html_page function

    POST request -> updates rated_recipes table depending on if a user decides
    to rate any of the recipes
    '''
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
        insert_rating_statement = "UPDATE rated_recipes SET rating = '%d' WHERE id\
                                = (SELECT MAX(id) FROM rated_recipes)"%(int(request.POST['rating'][-1]),)
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()
        c = c.execute(insert_rating_statement)
        connection.commit()
        connection.close()
        return redirect("/home/dashboard/past_recipes/")

class Change_User_Info(TemplateView):
    '''
    Allows users to change their information (i.e. name, weekly budget, etc.)

    GET request -> loads and displays our custom form that includes fields
    that users' can change

    POST request -> loops through the new information the user inputs and updates
    the fields in the user_signup_user_data table according to those new inputs.
    If a user inputs new dietary restrictions, it will delete their old inputted
    dietary restrictions and input the new ones into the user_diet table
    '''
    template_name = 'user_signup/user_preferences.html'
    def get(self, request):
        form = CustomForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        connection = sqlite3.connect('db.sqlite3')
        c = connection.cursor()

        for key, value in request.POST.lists():
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
                    delete_old_restrictions = "DELETE FROM user_diet WHERE user_id = ?"
                    c.execute(delete_old_restrictions, (request.user.id,))
                    field = 'dietary_restrictions'
                    for diet in value:
                        diet_statement = "INSERT INTO user_diet (dietary_restrictions, user_id) VALUES (?, ?)"
                        c.execute(diet_statement, (diet, request.user.id))
                    connection.commit()
                    break
                update_statement = "UPDATE user_signup_user_data SET " + field + " = '%s' WHERE user_id = '%s'"%(value[0], request.user.id)
                c = c.execute(update_statement)
                connection.commit()

        connection.close()
        messages.add_message(request, messages.SUCCESS, 'You have changed your preferences!')
        return redirect("/home/dashboard")

def register(request):
    '''
    Allows the user to register (i.e. create an account with a username/password)
    and calls a prebuilt django form called UserCreationForm that takes care of checking to make sure the
    two passwords are the same, as well as encrypts the passwords. Stores information in auth_user table.
    '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/home/login/")
        else:
            # if the inps ut is valid either due to unmatching passwords or username already taken
            form = UserCreationForm()
            messages.add_message(request, messages.ERROR, 'Input is invalid!')
            args = {'form':form}
            return render(request, 'user_signup/new_user.html', args)
    else:
        form = UserCreationForm()
        args = {"form":form}
        return render(request, 'user_signup/new_user.html', args)
