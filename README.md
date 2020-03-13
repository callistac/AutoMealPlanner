# AutoMealPlanner

Group project for CMSC 12200 that creates an automated, weekly meal planner based on
a user's dietary restrictions, budget, and more. 

ui -> this folder contains the files needed to create our django user interface, which allows a user to create an account and generate weekly meal plans pulled from www.allrecipes.com. Once in the ui folder, type `python manage.py runserver` to start the server and interact with our code. 

hpp_files -> this folder contains the results of the webscraping for the hyde park produce website to get estimates of pricing for groceries in the hyde park area, which will give our user an estimate of how much their weekly groceries will cost. The output of this webscraping is stored in hpp_products.csv, but is also converted into a SQL table that can be queried by our django webserver.

final_recipe_files -> this folder contains the csv files that were generated when scraping the www.allrecipes.com site. The actual scraping is done in the recipe_scraper.py file. 

test_recipe_files -> contains a short amount of test files that are a subset of final_recipe_files

make_grocery_list.py -> contains code linking the data from the final_recipe_files from the allrecipes.com scraping as well as the Hyde Park Produce scraping to be able to estimate the price of a given list of ingredients scraped from allrecipes.com

Proposal.pdf -> pdf of our mid-quarter proposal on this project

For more information on the code and structure of the django user interface itself, see the README in the ui folder. 

