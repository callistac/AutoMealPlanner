from User_Class import User

# An input is requested and stored in a variable
name = input ("Enter your first and last name: ")
name = str(name)

zipcode = input("Enter your zipcode: ")
zipcode = int(zipcode)

user = User(name, zipcode, [])
