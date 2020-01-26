from User_Class import User

weekly_budget_update = input("Any changes to your weekly budget? (enter YES or NO): ")
if weekly_budget_update.lower() == 'yes':
    print("Updated!")
    #update user class

laziness = input("How much time do you have for meal prep this week? (enter a number\
between 0 and 5, with 5 being as much time as needed, and 0 being no time): ")
