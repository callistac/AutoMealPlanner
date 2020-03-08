from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib import messages
from user_signup.generate_recipes import generate_html_page
from django.http import HttpResponse
import sqlite3
import numpy as np

def query_recipes(user_info):
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
    prep_time = str((6-int(user_info[6]))*5 + 5)
    sql_recipes = "SELECT * FROM recipes WHERE prep_time < ? ORDER BY RANDOM() LIMIT 7;"
    print(user_info)
    c.execute(sql_recipes, [prep_time])
    recipes = c.fetchall()
    ids = tuple([x[0] for x in recipes])
    #make sure recipe is not in blacklisted recipes!
    #CODE HERE
    
    c.execute("select ingred_codes.name from ingred_codes join recipe_ingred ON recipe_ingred.ingredient_id = ingred_codes.ingredient_id where recipe_num in {}".format(ids))
    ingred = c.fetchall()
    print(ingred)
    print(recipes)
    return recipes, ingred
