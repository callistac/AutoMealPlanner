from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from django.http import HttpResponse
import sqlite3
import numpy as np

def query_recipes(user_info, blacklist, past_recipes, past_ingredients):
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
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
    print("PREPTIME", (prep_time))
    if past_recipes is None:

        sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? AND (recipe_num not in \
        (SELECT recipe_num FROM blacklisted_recipes WHERE user_id = ? AND \
        (reason = 'option1' OR reason = 'option2')) OR (\
        SELECT recipe_num FROM rated_recipes WHERE user_id = ? AND \
        (rating = 1 OR rating = 2))) ORDER BY RANDOM() LIMIT 7;"

        #sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? ORDER BY RANDOM() LIMIT 7;"
        c.execute(sql_recipes, [prep_time, user_info[7], user_info[7]])
        #c.execute(sql_recipes, [prep_time,])

        recipes = c.fetchall()
        ids = tuple([x[0] for x in recipes])
        c.execute("select recipe_ingred.recipe_num, ingred_codes.name from ingred_codes join recipe_ingred ON recipe_ingred.ingredient_id = ingred_codes.ingredient_id where recipe_num in {}".format(ids))
        ingred = c.fetchall()
        return recipes, ingred
    else:

        sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? AND (recipe_num not in \
        (SELECT recipe_num from blacklisted_recipes where user_id = ? AND \
        (reason = 'option1' OR reason = 'option2')) OR (\
        SELECT recipe_num FROM rated_recipes WHERE user_id = ? AND \
        (rating = 1 OR rating = 2))) ORDER BY RANDOM() LIMIT 1;"

        #sql_recipes = "SELECT * FROM recipes WHERE prep_time <= ? ORDER BY RANDOM() LIMIT 1;"
        #c.execute(sql_recipes, [prep_time,])

        c.execute(sql_recipes, [prep_time, user_info[7], user_info[7]])
        new_recipe = c.fetchone()
        index = past_recipes.index([x for x in past_recipes if blacklist[0] in x][0])
        past_recipes[index] = (list(new_recipe))
        c.execute("select recipe_ingred.recipe_num, ingred_codes.name from ingred_codes join recipe_ingred ON recipe_ingred.ingredient_id = ingred_codes.ingredient_id where recipe_num = ?", (new_recipe[0],))
        new_ingred = [list(x) for x in c.fetchall()]
        ingred_no_blacklist = [y for y in past_ingredients if blacklist[0] not in y]
        ingred_no_blacklist += new_ingred
        return past_recipes, ingred_no_blacklist
