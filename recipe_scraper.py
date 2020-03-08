import requests
import json
import re
import csv
import bs4
import sys
import unicodedata
import pandas as pd
import url_util
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


UNIT_LIST = ['cup', 'tablespoon', 'teaspoon', 'ounce', 'oz', 'lb', 'pound', \
        'pint', 'clove', 'leaf', 'quart', 'gallon', 'gram', 'g', 'ml', \
        'milliliter', 'fl. ounce', 'tsp', 'tbsp', 'T', 't', 'can', 'package', \
        'slice', 'sprig', 'bunch', 'packet', 'container', 'cups', 'tablespoons', \
        'teaspoons', 'ounces','lbs', 'pounds', 'pints', 'cloves', 'leaves', \
        'quarts', 'gallons', 'grams', 'g', 'ml', 'milliliters', 'fl. ounces', \
        'fluid ounces',' cans', 'packages', 'slices', 'sprigs', 'bunches', \
        'packets', 'containers', 'dash', 'pinch', 'dashes', 'pinches', 'box', \
        'bulb', 'sheet', 'sheets', 'bottle', 'bottles', 'jar', 'jars']

BAD_CATS = ["Dessert", "Drink", "Smoothie", "Bread", "Desserts", "Candy", \
        "Cookie", "Cookies", "Drinks", "Candies", "Breads", "Smoothies", "Pie", \
        "Pies", "Sauce", "Sauces", "Condiment", "Condiments", "Dip", "Dips"]

GOOD_CATS = ["Dinner", "Italian Inspired", "Beef", "Pork", "Seafood", \
        "World Cuisine", "European", "Italian", "Main Dishes", "Pasta", \
        "Pasta and Noodles", "Vegan", "Vegetarian", "Asian", "Quick Easy", \
        "Casserole", "Breakfast", "Soup", "World", "Health", "Holiday", \
        "Appetizer", "Mexican", "South American", "African", "BBQ", \
        "Dairy Free", "Slow", "Side", "Main", "Lunch", "Salad", \
        "Gluten Free", "Indian", "Thai", "Chinese", "Canadian", "French", \
        "Japanese", "Korean", "Mediterranean", "American", "Middle Eastern", \
        "Latin American", "Halal", "Kosher"]


#from pa2
def get_urls(url, queue_list, visited, links, limiting_domain):
    '''
    Finds all valid urls on current page and adds them to the queue in-place

    Inputs:
        url (string): current url
        queue_list (list of strings): list of currently queued urls
        visited (list of strings): list of urls already visited
        links (list of tags): list of all 'a' tags on current page
        limiting_domain (string): the limiting domain

    Outputs:
        Modifies queue_list in-place with the new pages to be visited
    '''
    for i in links:
        if i.has_attr('href'):
            absolute_link = url_util.convert_if_relative_url(url, i['href'])
            if absolute_link:
                absolute_link = url_util.remove_fragment(absolute_link)
                ok = url_util.is_url_ok_to_follow(absolute_link, limiting_domain)
                if ok and (absolute_link not in (visited + queue_list)) and \
                        (absolute_link != url):
                    queue_list.append(absolute_link)


def get_ingredient(ingredient_string):
    try:
        unicode_frac = unicodedata.numeric(ingredient_string[0])
        count = re.search(r"^(\d*\s?(\d*)\/?\.?(\d+?))", ingredient_string)
        unit_regex = "(" + "|".join(UNIT_LIST) + ")s?"

    except:
        unicode_frac = None
        count = re.search(r"^(\d*\s?(\d*)\/?\.?(\d+?))", ingredient_string)
        unit_regex = "(" + "|".join(UNIT_LIST) + ")s?"

    if count or unicode_frac:

        if count:
            count = count.group()
            count_str = count
            ingredient = ingredient_string[len(count) + 1:]
            try:
                unicode_frac2 = unicodedata.numeric(ingredient[0])
                count = float(count) + unicode_frac2
                ingredient = ingredient[2:]

            except:
                unicode_frac2 = None

        else:
            count = unicode_frac
            count_str = ingredient_string[0]
            ingredient = ingredient_string[2:]
            unicode_frac2 = None

        try:
            count = float(count)

        except:
            num_list = count.split(" ")
            try:
                if len(num_list) == 2:
                    numer, denom = num_list[1].split("/")
                    count = float(num_list[0]) + float(numer)/float(denom)

                else:
                    numer, denom = num_list[0].split("/")
                    count = float(numer)/float(denom)
            except:
                count = int(num_list[0])
                ingredient = ingredient[len(num_list[0]) + 1:]
        search = re.search("\\(\\d*\\.?\\d+(\sfluid)? (ounce|pound)\\)", ingredient)

        if search:
            search = search.group()
            size, units = search.strip("()").split(" ")
            units = units.strip("s")
            amount = round(count * float(size), 7)
            ingredient = ingredient[len(search)+1:]
            first_word = ingredient.split(" ")[0]
            secondary_unit = re.fullmatch(unit_regex, first_word)

            if secondary_unit:
                secondary_unit = secondary_unit.group()
                #this secondary unit can be ignored, as the unit found above
                #supercedes it -- knowing the ingredient is measured in ounces
                #is more useful than knowing the recipe calls for 2 cans of it,
                #for example

                ingredient = ingredient[len(secondary_unit)+1:]
        else:
            amount = float(count)
            if ingredient and unicode_frac2:
                first_word = ingredient.split(" ")[0]
            else:
                first_word = ingredient_string[len(count_str)+1:].split(" ")[0]

            units = re.fullmatch(unit_regex, first_word)

            if units:
                units = units.group().rstrip("s")
                ingredient = ingredient[len(units)+1:]

            else:
                units = "None"

    else:
        amount = "NaN"
        first_word = ingredient_string.split(" ")[0]
        units = re.fullmatch(unit_regex, first_word)

        if units:
            units = units.group().strip("s")
            ingredient = ingredient_string[len(units)+1:]

        else:
            units = "None"
            ingredient = ingredient_string

    return ingredient.strip(" "), amount, units


#modified from pa2 code
def add_to_csvs(ingredients, categories, image, title, rec_num, link, \
        servings, times, n_reviews, avg_review, ingred_filename, \
        ingred_code_filename, cat_filename, main_filename):
    '''
    Pulls the relevant info out of each tag object and adds it to the index

    Inputs:

    Outputs:
        Adds current page's info for each tag to the index dictionary in-place
    '''
    main_csv = open(main_filename, "a")
    ingred_csv = open(ingred_filename, "a")
    cat_csv = open(cat_filename, "a")
    i_codes = pd.read_csv(ingred_code_filename, delimiter = "|", \
            index_col = "ingredient_id")

    for code in ingredients.keys():
        ingredient, amount, units = get_ingredient(ingredients[code])
        code = int(code)

        if code not in i_codes.index:
            i_codes.loc[code] = ingredient

        elif len(i_codes.loc[code, 'name']) > len(ingredient):
            i_codes.loc[code, 'name'] = ingredient

        ingred_csv.write("\n" + str(rec_num) + "|" + str(amount) + "|" + \
                units + "|" + str(code))

    for category in categories:
        cat_csv.write("\n" + str(rec_num) + "|" + category)

    main_csv.write("\n" + str(rec_num) + "|" + str(title) + "|" + str(link) + \
            "|" + str(image) + "|" + str(servings) + "|" + str(times[0]) + \
            "|" + str(times[1]) + "|" + str(times[2]) + "|" + str(n_reviews) + \
            "|" + str(avg_review))

    main_csv.close()
    ingred_csv.close()
    cat_csv.close()
    i_codes.to_csv(ingred_code_filename, index_label = "ingredient_id", \
            sep = "|", mode = "w")


#from pa2
def generate_csvs(main_filename, ingred_filename, ingred_index_filename, \
        cat_filename):
    '''
    '''
    with open(main_filename, 'w') as main_csv:
        main_csv.write("recipe_num|title|url|image|servings|prep_time|" + \
                "cook_time|total_time|n_reviews|avg_review")
        main_csv.close()


    with open(ingred_filename, 'w') as ingred_csv:
        ingred_csv.write("recipe_num|amount|unit|ingredient_id")
        ingred_csv.close()


    with open(ingred_index_filename, 'w') as i_codes_csv:
        i_codes_csv.write("ingredient_id|name")
        i_codes_csv.close()


    with open(cat_filename, 'w') as cat_csv:
        cat_csv.write("recipe_num|category")
        cat_csv.close()


#modified from pa2 code
def split_by_tag_type(parsedhtml):
    '''

    '''
    links = []
    ingredients = {}
    title = None
    image = None
    categories = []
    times = [None, None, None]
    servings = None
    avg_review = 0
    n_reviews = 0
    for tag in parsedhtml:
        if tag.name == 'a':
            links.append(tag)

        elif tag.name == 'label' and tag.has_attr("ng-class") and \
                "{true: 'checkList__item'}[true]" in tag["ng-class"]:
            ingredients[tag.next_element.next_element["data-id"]] = tag["title"]

        elif tag.name == 'label' and tag.has_attr("class") and \
                "checkbox-list" in tag["class"]:
            parent = tag.find_parent()
            if parent.has_attr("data-id"):
                ingredients[int(tag.find_parent()["data-id"])] = \
                        tag.findChild("span", {"class": \
                        "ingredients-item-name"}).text.strip()

        elif tag.name == "img" and not image and tag.has_attr("class") and \
                "rec-photo" in tag["class"]:
            image = tag["src"]

        elif tag.name == "div" and not image and tag.has_attr("class") and\
                "lead-media" in tag["class"]:
            image = tag["data-src"]

        elif tag.name == "title" and not title:
            title = tag.text.split(" Recipe - Allrecipes.com")[0]

        elif tag.name == 'script':
            search = re.search(r"var RdpInferredTastePrefs = \[.+\]", tag.text)
            if search:
                cats = (re.findall("\"\w+\s?\w*\"", search.group()))
                for cat in cats:
                    categories.append(cat.strip("\""))

        elif tag.name == 'div' and tag.has_attr("class") and \
                "keyvals" in tag["class"]:
                    categories.extend(tag["data-content_cms_tags"].split("|"))
                    categories.extend(tag["data-content_cms_category"].split(","))

        elif tag.name == 'div' and tag.has_attr("class") and \
                "recipe-meta-item-header" in tag["class"]:
            text = tag.text.strip()
            if text in ["prep:", "cook:", "total:"]:
                substrings = tag.fetchNextSiblings()[0].text.strip().split(" ")

                time_list = []
                unit_list = []
                for s in substrings:
                    try:
                        s = float(s)
                        time_list.append(s)
                    except:
                        unit_list.append(s)

                time = 0

                for i, value in enumerate(time_list):
                    if unit_list[i] in ["days", "day", "d"]:
                        time += value * 24 * 60

                    elif unit_list[i] in ["hrs", "hr", "h", "hour", "hours"]:
                        time += value * 60

                    elif unit_list[i] in ["mins", "min", "m", "minute", "minutes"]:
                        time += value

                    else:
                        print(unit_list[i], value)

                if text == "prep:":
                    times[0] = int(time)

                elif text == "cook:":
                    times[1] = int(time)

                else:
                    times[2] = int(time)

            elif text == "Servings:":
                servings = int(tag.fetchNextSiblings()[0].text.strip())

        elif tag.name == "meta" and tag.has_attr("id") and tag["id"] == \
                "metaRecipeServings":
            servings = int(tag["content"])

        elif tag.name == "time":
            regex = r"\d+"
            regex2 = r"[a-zA-z]+"
            times_list = re.findall(regex, tag["datetime"])
            units_list = re.findall(regex2, tag["datetime"])

            if len(times_list) == 2 and units_list[1] == "H" and \
                    units_list[2] == "M":
                time = (int(times_list[0]) * 60) + (int(times_list[1]))

            elif len(times_list) == 2 and (units_list[1] == "Day" or \
                    units_list[1] == "Days") and units_list[2] == "H":
                time = ((int(times_list[0]) * 24 + int(times_list[1])) * 60)

            elif len(times_list) == 2 and (units_list[1] == "Day" or \
                    units_list[1] == "Days") and units_list[2] == "M":
                time = (int(times_list[0]) * 24 * 60) + (int(times_list[1]))

            elif len(times_list) == 1 and units_list[1] == "M":
                time = int(times_list[0])

            elif len(times_list) == 1 and units_list[1] == "H":
                time = int(times_list[0]) * 60

            elif len(times_list) == 1 and (units_list[1] == "Day" or \
                    units_list[1] == "Days"):
                time = int(times_list[0]) * 24 * 60

            elif len(times_list) == 3:
                time = ((int(times_list[0]) * 24 + int(times_list[1])) * 60) + \
                        int(times_list[2])

            else:
                print(times_list, tag)

            if tag["itemprop"] == "prepTime":
                times[0] = time

            elif tag["itemprop"] == "cookTime":
                times[1] = time

            else:
                times[2] = time

        elif tag.name == "div" and tag.has_attr("class") and \
                "recipe-reviews" in tag["class"]:
            if tag.has_attr("data-ratings-count") and tag["data-ratings-count"] \
                    and tag.has_attr("data-ratings-average") and \
                    tag["data-ratings-average"]:
                n_reviews = int(tag["data-ratings-count"])
                avg_review = float(tag["data-ratings-average"])

        elif tag.name == "span" and tag.has_attr("itemprop") and \
                tag["itemprop"] == "aggregateRating":
            children = tag.findChildren()
            for child in children:
                if child["itemprop"] == "ratingValue":
                    avg_review = float(child["content"])

                elif child["itemprop"] == "reviewCount":
                    n_reviews = int(child["content"])

    return links, ingredients, image, title, categories, times, servings, \
            n_reviews, avg_review


#modified from pa2 code
def go(num_recipes_to_scrape, ingred_filename, ingred_code_filename, \
        cat_filename, main_filename):
    '''
    Crawl the college catalog and generate a CSV file with an index.

    Inputs:
        num_pages_to_crawl (int): the number of pages to process
            during the crawl

    Outputs:
        CSV file of the index
    '''
    #starting_url = "https://www.allrecipes.com/recipe/8711/island-chicken-with-fruit-salsa/"
    starting_url = "https://www.allrecipes.com/"
    limiting_domain = "www.allrecipes.com"
    generate_csvs(main_filename, ingred_filename, ingred_code_filename, \
            cat_filename)
    queue_list = [starting_url]
    visited = []
    n_recipes = 0

    while len(visited) < num_recipes_to_scrape and queue_list != []:
        #does html request on head of the queue
        request = url_util.get_request(queue_list.pop(0))
        if request:
            #reads html from the request and gets the redirect url
            request_html = url_util.read_request(request)
            request_url = url_util.get_request_url(request)
            ok = url_util.is_url_ok_to_follow(request_url, limiting_domain)
            if ok and request_url not in (queue_list + visited):
                visited.append(request_url)
                print("Visited: " + str(len(visited)) + "/" + \
                        str(len(queue_list+visited)) + " at " + request_url)
                #collects tags required for the crawler and indexer
                soup = bs4.BeautifulSoup(request_html, "html5lib")
                parsedhtml = soup.find_all({"a": True, "label": True,
                        "script": True, "div": True, "time": True, "meta": True, \
                        "span": True, "img": True, "title": True})
                links, ingredients, image, title, categories, times, servings, \
                        n_reviews, avg_review = split_by_tag_type(parsedhtml)
                if n_reviews >= 15 and avg_review >= 3.5 and categories:
                    rec_num = re.search(r"\d+", request_url).group()

                    #adds current page info to the index if it's a recipe page
                    add_recipe = True
                    for cat in BAD_CATS:
                        if cat in categories:
                            add_recipe = False
                            break

                    if add_recipe:
                        add_to_csvs(ingredients, categories, image, title, \
                                rec_num, request_url, servings, times, n_reviews, \
                                avg_review, ingred_filename, \
                                ingred_code_filename, cat_filename, \
                                main_filename)

                        n_recipes += 1
                        print(str(n_recipes) + ": " + title)
                        #print(request_url)
                        #print(rec_num)
                        #print(servings)
                        #print(times)
                        #print(ingredients)
                        #print(image)
                        #print("    categories: " + str(categories))
                        print("")
                        #queues up all valid urls on current page

                get_urls(request_url, queue_list, visited, links, limiting_domain)

    '''
    print(main_index)
    print("")
    print(ingred_index)
    print("")
    print(ingred_code_index)
    print("")
    print(cat_index)
    print("")
    print(len(visited))
    '''


#from pa2
if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    ingred_filename = "test_recipe_ingredients.csv"
    ingred_code_filename = "test_ingredient_codes.csv"
    cat_filename = "test_recipe_categories.csv"
    main_filename = "test_recipes.csv"
    if args_len == 1:
        num_recipes_to_scrape = 1000000
    elif args_len == 2:
        try:
            num_recipes_to_scrape = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_recipes_to_scrape, ingred_filename, ingred_code_filename, \
            cat_filename, main_filename)
