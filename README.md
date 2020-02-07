# AutoMealPlanner

Group project for CS 12200 that creates an automated, weekly meal planner based on
a user's dietary restrictions and budget

Update_db.sql -> series of SQL commands that add users/allergies to corresponding tables

Use the following commands to access the existing databases and add rows to the databases
`sqlite3 Databases/combined.db 
sqlite> .read Update_db.sql`

Table_schema -> file that creates table schema for user, allergies, and recipies tables

Interact_w_User.py -> file that allows user to interact (type) with the command line (i.e. input your name)
Weekly_Checkup.py -> info that we will want to ask the user on a weekly basis before creating a new meal plan for them (i.e. did their budget update?
User_Class.py -> the file that contains the user class 
