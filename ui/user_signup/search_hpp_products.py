'''
CS 122 Winter '20 Group Project
The function find_product matches the ingredients of a receipe to the products
online at Hyde Park Produce. It will return the product row from the
HPP_Products SQL table.
'''
import sqlite3
import os
import jellyfish
import re

# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR+"/../", "db.sqlite3")
#brands contains the names of brands and other words we want to ignore
brands = ["Kellogg's", "General Mills", "Malt-O-Meal", "Nestlé", "Quaker Oats",
            "Post Foods", "Frito Lay", "Oreo", "Campbell's", "Cheerios",
            "Betty Crocker", "Heinz", "Pillsbury", "Ritz", "Hershey", "Cabot",
            "Kerrygold", "Chobani", "Pure", "Irish", "Lakewood",
            "Organic Valley", "Organic", "Fresh", "Pressed", "Valley",
            "Spice Supreme", "Filippo Berio", "Whole", "Diamond Crystal",
            "Kosher", "Birds Eye", "Dean Jacobs", "Grinder Mill",
            "North Atlantic", "Kikkoman", "Dynasty", "Sauders Amish",
            "Eggland's", "Eggland", "Kelloggs", "Bulbs", "(Loose)",
            "Imperial", "Bags", "Ancient Harvest", "Vigo", "Authentic",
            "La Preferida", "Inca Red Grains", "Royal Bolivian",
            "Bobs Red Mill", "Fritos", "Domino", "Pure Cane", "Idaho",
            "Quick Dissolve Superfine", "(Loose)", "Bags", "Cabot",
            "All-Purpose", "Unbleached", "Prairie Farms", "Michigan",
            "King Arthur Flour", "valley", "Boars Head", "Boar's Head",
            "Sassy Cow Creamery", "Alessi", "chopped", ", Laney Honey",
            "Wildflower ", "Gia Russa Pasta Sauce", "Spice Hunter", "Genova",
            "Cento", "Solid Pack Light", "Solid Light", "Perdue", "CF Burger",
            "Applegate Naturals", "Farmer Focus ", "Free Range", " Boneless ",
            " Skinless "]
#when seperating the words in an ingredient,
#do not match to products with words in cantmatchon
cantmatchon = ["black", "white", "sliced", "large", "head", "extract",
                "chopped", "cooking"]
#rewording very common ingredients that can't match to the actual product
commonfailures = ["brown sugar", "cream", "beef"]
shouldmatch = ["sugar%brown", "Heavy Whipping Cream", "ground beef"]

#MOVE THIS FN TO A UTILS FILE
def remove_from_string(remove, string, removeposition = ""):
    removeobj = re.search(remove, string)
    if removeobj != None:
        if removeobj.end() == len(string) or removeposition == \
            "everythingafter":
            string = string[:removeobj.start()]
        elif removeposition == "everythingbefore":
            string = string[removeobj.end():]
        elif removeposition == "":
            string = string[:removeobj.start()] + string[removeobj.end():]
    return string


def match_ingredient_to_product(ingredient):
    """
    Generates a query and arg list to look for Products with names that
        contain the ingredient string.

    inputs: ingredient (string): an ingredient to match with the Products

    outputs: tuple of:
                query_string (string): SQL query string
                arg_list (list): arguments for the SQL query
    """
    #query_string = "SELECT Ingredients FROM Recipes WHERE Name LIKE ?;"
    query_string = "SELECT * FROM HPP_Products WHERE Product LIKE ?;"
    if ingredient in commonfailures:
        for n in range(len(commonfailures)):
            if commonfailures[n] == ingredient:
                ingredient = shouldmatch[n]
    arg_list = ["%"+ingredient+"%"]
    return (query_string, arg_list)


def generate_query_string(recipe_ingredient):
    '''
    Takes a list of ingredients and generates an SQL query for each one
    that will return Products that match ingredient string.

    input: recipe_ingredients (list): list of the ingredients for a receipe

    output: queries_and_args (tuple) of:
                query_string (string): SQL query string
                arg_list (list): arguments for the SQL query
    '''
    query_and_args = match_ingredient_to_product(recipe_ingredient)
    return query_and_args


def find_product(recipe_ingredient):
    '''
    Matches ingredients to products online at Hyde Park Produce. Prefers a
    direct match of the whole ingredient string, if none exist, splits the
    ingredient up into seperate words. Then matches those to products, favors
    the products that match the most individual words.
    For the products returned in both processes, we remove brand names and then
    compute a Jaro_Winkler score and return the product with the highest.

    input: recipe_ingredients (list): list of the ingredients for a receipe

    output: bestmatches (list): names of products that correspond
                                to recipe_ingredients
    '''

    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query_string, arg_list = generate_query_string(recipe_ingredient)

    bestmatches = []
    query = c.execute(query_string, arg_list)
    fetch = query.fetchall()

    matchscore = 0
    maxcount = 0
    longest_fetch_len = 0
    longest_fetch = []
    otherfetches = []
    if fetch == []:
	    #leave bestmatch as None in case new search still doesn't turn up results
	    bestmatch = None
	    newargs = arg_list[0][1:len(arg_list[0])-1].split(" ")
	    all_fetches = []
	    combinedfetches = []
	    for newarg in newargs:
		    query = c.execute(query_string, ["%"+newarg+"%"])
		    fetch = query.fetchall()
		    if newarg in cantmatchon:
			    otherfetches.append(fetch)
			    fetch = []
		    else:
			    all_fetches.append(fetch)

	    for fetch in all_fetches:
		    if longest_fetch_len < len(fetch):
			    longest_fetch_len = len(fetch)
			    longest_fetch = fetch

	    for fetch in all_fetches:
		    if fetch not in longest_fetch:
			    otherfetches.append(fetch)

	    for fetch in longest_fetch:
		    count = 0
		    for otherfetch in otherfetches:
			    if fetch in otherfetch:
				    count += 1
		    if count > maxcount:
			    maxcount = count
			    combinedfetches = []
		    if count >= maxcount:
			    combinedfetches.append(fetch)
	    if maxcount == 0:
		    for otherfetch in otherfetches:
			    for fetch in otherfetch:
				    combinedfetches.append(fetch)

	    for product in combinedfetches:
		    cleanproduct = product[0]
		    cleanarg = arg_list[0][1:len(arg_list[0])-1]
		    for brand in brands:
			    if re.findall(brand, cleanproduct) != []:
				    cleanproduct = remove_from_string(brand, cleanproduct)
				    #cleanproduct = remove_from_string(, cleanproduct)
				    cleanproduct = remove_from_string(",", cleanproduct)
			    if re.findall(brand, arg_list[0][1:len(arg_list[0])-1]):
				    cleanarg = remove_from_string(brand, cleanarg)
		    jaroval = jellyfish.jaro_winkler(cleanarg, cleanproduct)
		    #print(arg_list[0][1:len(arg_list[0])-1], cleanproduct, jaroval)
		    if jaroval > matchscore:
			    matchscore = jaroval
			    bestmatch = product

    else:
	    for product in fetch:
		    cleanproduct = product[0]
		    for brand in brands:
			    if re.findall(brand, cleanproduct) != []:
				    cleanproduct = remove_from_string(brand, cleanproduct)
				    cleanproduct = remove_from_string(",", cleanproduct)

		    jaroval = jellyfish.jaro_winkler(arg_list[0], cleanproduct)
		    #if jaroval > 0.5:
		    #  print(arg_list[0][1:len(arg_list[0])-1], cleanproduct, jaroval)
		    if jaroval > matchscore:
			    matchscore = jaroval
			    bestmatch = product

    db.close()
    return bestmatch
