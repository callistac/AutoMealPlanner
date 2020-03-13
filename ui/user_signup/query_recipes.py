from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from django.http import HttpResponse
import sqlite3
import numpy as np

def query_recipes(user_info, blacklist, past_recipes, past_ingredients):
    '''
    Queries recipes based on user preferences (how long they would like to spend on meal prep, Weekly budget, etc.).
    This query also does not display recipes that a user has blacklisted (i.e. the recipe displayed
    does not fulfill their dietary restrictions or it looks disgusting- option 1 or 2) or if they have rated
    any past recipes poorly (i.e. rating 1 or 2). If a user is blacklisting (deselecting) a recipe, we will just
    perform a query for that one recipe and will keep the others the same.

    Input:
        user_info (list) -> user_info[6] is the "effort" the person is willing to put into meal prep for that week
        blacklist (list) -> list of ID for a recipe that they are blacklisting (i.e. we just want to perform a query
                            for that one recipe)
        past_recipes (list) -> either None if the user has never generated recipes yet or a list of the user's past menu
                                generation
        past_ingredients (list) -> either None if the user has never generated recipes yet or a list of the user's
                                    ingredients based on their past recipes
    Output:
        returns queried recipes and ingredients for that week
    '''
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
    c.execute("SELECT dietary_restrictions FROM user_diet WHERE user_id = ?", (user_info[7], ))
    diet_rest = c.fetchall()
    print("DIETARYYY", diet_rest)
    query = "(SELECT recipe_num FROM recipe_cats WHERE"
    for i, restriction in enumerate(diet_rest):
        query += " recipe_cats.category = '%s' OR"%(restriction[0])
    query = query[:-3]
    query += ")"
    print("QUERY", query)
    # finding prep-time for how lazy the user input into our form for that week
    if user_info[6] == '1':
        prep_time = 15
    elif user_info[6] == '2':
        prep_time = 35
    elif user_info[6] == '3':
        prep_time = 45
    elif user_info[6] == '4':
        prep_time = 60
    else:
        prep_time = 90

    # if a user has never generated past recipes before
    if past_recipes is None:
        sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? AND (recipes.recipe_num IN" + query + ") AND (recipe_num not in \
        (SELECT recipe_num FROM blacklisted_recipes WHERE user_id = ? AND \
        (reason = 'option1' OR reason = 'option2')) OR (\
        SELECT recipe_num FROM rated_recipes WHERE user_id = ? AND \
        (rating = 1 OR rating = 2))) ORDER BY RANDOM() LIMIT 7;"

        c.execute(sql_recipes, [prep_time, user_info[7], user_info[7]])
        recipes = c.fetchall()
        ids = tuple([x[0] for x in recipes])
        c.execute("SELECT recipe_ingred.recipe_num, ingred_codes.name FROM ingred_codes JOIN \
         recipe_ingred ON recipe_ingred.ingredient_id = ingred_codes.ingredient_id WHERE recipe_num in {}".format(ids))
        ingred = c.fetchall()
        return recipes, ingred

    # if a user has generated past recipes before (i.e. potentially has blacklisted or rated recipes)
    else:
        sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? AND (recipes.recipe_num IN" + query + ") AND (recipe_num not in \
        (SELECT recipe_num from blacklisted_recipes where user_id = ? AND \
        (reason = 'option1' OR reason = 'option2')) OR (\
        SELECT recipe_num FROM rated_recipes WHERE user_id = ? AND \
        (rating = 1 OR rating = 2))) ORDER BY RANDOM() LIMIT 1;"

        c.execute(sql_recipes, [prep_time, user_info[7], user_info[7]])
        new_recipe = c.fetchone()
        index = past_recipes.index([x for x in past_recipes if blacklist[0] in x][0])
        past_recipes[index] = (list(new_recipe))
        c.execute("SELECT recipe_ingred.recipe_num, ingred_codes.name FROM ingred_codes JOIN\
         recipe_ingred ON recipe_ingred.ingredient_id = ingred_codes.ingredient_id WHERE recipe_num = ?", (new_recipe[0],))
        new_ingred = [list(x) for x in c.fetchall()]
        ingred_no_blacklist = [y for y in past_ingredients if blacklist[0] not in y]
        ingred_no_blacklist += new_ingred
        return past_recipes, ingred_no_blacklist
