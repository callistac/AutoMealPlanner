# AutoMealPlanner

Group project for CMSC 12200 that creates an automated, weekly meal planner based on
a user's dietary restrictions, budget, and more. 

ui -> this folder contains the files needed to create our django user interface, which allows a user to create an account and generate weekly meal plans pulled from www.allrecipes.com. 

grocery_csv_generator.py -> this file webscrapes the hyde park produce website to get estimates of pricing for groceries in the hyde park area, which will give our user an estimate of how much their weekly groceries will cost. The output of this webscraping is stored in hpp_products.txt, but is also converted into a SQL table that can be queried by our django webserver.

For more information on the code and structure of the django user interface itself, see the README in the ui folder. 

