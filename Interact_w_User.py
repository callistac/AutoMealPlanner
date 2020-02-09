from User_Class import User

# This is code for the initial interaction between a user and the program
name = input("Enter your first and last name: ")
name = str(name)

zipcode = input("Enter your zipcode: ")
zipcode = int(zipcode)

user = User(name, zipcode, [])
