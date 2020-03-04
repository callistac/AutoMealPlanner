Managed by Katya Gozman and Callista Christ

This django web interface allows our user to interact with our automated meal algorithm. Our web interface prompts a user to create an account, which stores information such as their username, password, name, zipcode, email, dietary restrictions, weekly budget, and how much effort they are willing to put into meals.

Once the user enters their information and their information is valid, they are prompted to the login screen (http://127.0.0.1:8000/home/login). Once they log in, they are prompted to the dashboard screen (http://127.0.0.1:8000/home/dashboard/) where they can generate a new weekly meal plan by clicking the "Generate New Weekly Menu" button.

The generation of meals occurs on the http://127.0.0.1:8000/home/dashboard/meals/ webpage. If the user likes the recipes that are automatically generated for them at the bottom of the page, they are able to click the "Generate Grocery List" button to automatically generate their list of recipes for that week, along with an estimated price of groceries for that week. If the user is unsatisfied with a recipe, they are able to select the "Deselect Recipe" button, which will prompt them to fill out a new form as to why they are deselecting that recipe (i.e. was it based on dietary restrictions, did it just look gross, etc).

Once a recipe is deselected, a new random recipe will be displayed on the screen to replace the old one, along with the other recipes that existed previously. A user may deselect recipes as many times as they would like, and when they are satisfied they can simply select the "Generate Grocery List" button, as aforementioned.
