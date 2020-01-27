

class User(object):
    def __init__(self, name, zipcode, allergies, meal_types, weekly_budget):
        self.name = name
        self.zipcode = str(zipcode)
        self.highly_rated = []
        self.allergies = allergies
        self.cuisines = []
        self.meal_types = []
        self.items_in_kitchen = []
        self.weekly_budget = weekly_budget

    # records highly rated recipes that the user likes each week
    def get_highly_rated_recipes(self, recipe_link, rating):
        """
        Input:
            recipe_link (string): link to the highly rated recipe
            rating (int): 1 out of 5, 5 being that the user loved the recipe
                        or thought it looked tasty
        """
        self.highly_rated.append((recipe_link, rating))

    # finds a nearby store to get accurate price estimates for groceries
    def find_nearby_stores(self):
        """
        Input: self
        """
        self.zipcode
