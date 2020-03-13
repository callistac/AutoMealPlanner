*Managed by Katya Gozman and Callista Christ*

*** Note: see table_schema file for information on the SQL tables we used for project and their respective schema, all tables are saved to the db.sqlite3 database in the ui folder ***
*** Note 2: all html webpage files are listed in templates/user_signup. 'base_html' file is applied to all of the corresponding html files ***

This django web interface allows our user to interact with our automated meal algorithm. Our web interface prompts a user to create an account with us, and encrypts their password as well as makes sure that their username is not already taken by another user. It also checks to make sure their password is not a commonly used/bad password such as  "password1234".

Once the user enters their username and password and their information is valid, they are prompted to the login screen (http://127.0.0.1:8000/home/login). Once they log in, they are prompted to the dashboard screen (http://127.0.0.1:8000/home/dashboard/). If a user has not yet filled out information on their name, zipcode, email, dietary restrictions, weekly budget, and how much effort they are willing to put into meal prep each week, they will be prompted to do so on the dashboard. If the user has already filled out this information and is not logging in for the first time, then the dashboard will display a webpage allowing them to generate a new weekly meal plan by clicking the "Generate New Weekly Menu" button.

The generation of meals occurs on the http://127.0.0.1:8000/home/dashboard/meals/ webpage. If the user likes the recipes that are automatically generated for them at the bottom of the page, they are able to click the "Generate Grocery List" button to automatically generate their list of groceries for that week, along with an estimated price for those groceries (they can save this file to any location on their personal computer, default name is 'grocery_list.txt'). If the user is unsatisfied with a recipe, they are able to select the "Deselect Recipe" button, which will prompt them to fill out a new form as to why they are deselecting that recipe (i.e. was it based on dietary restrictions, did it just look gross, etc).

Once a recipe is deselected, a new random recipe will be displayed on the screen to replace the old one, along with the other recipes that existed previously. A user may deselect recipes as many times as they would like, and if they want to replace the whole list of recipes, they may refresh the page. When they are satisfied they can simply select the "Generate Grocery List" button, as aforementioned.

Once the user has generated recipes, they can logout. When they log back in, if they want to see the recipes that were given to them last week, they can click the "Generate Past Recipes" button on the dashboard page which will take them to http://127.0.0.1:8000/home/dashboard/past_recipes/. Here they can rate recipes that they have tried from last week, and if they rate the recipe a "1" or "2", we will refrain from showing them that recipe again.

A user has the ability to change their information regarding name, dietary restrictions, weekly budget, etc. by selecting the "Hello, [username]" link in the navigation bar on the top right of the screen (next to the sign out buttom).
We will update their information in the database accordingly.

Check out our home page (http://127.0.0.1:8000/home/) or about page (http://127.0.0.1:8000/home/about/) to learn more about this project!
