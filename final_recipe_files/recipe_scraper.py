'''
Modification and extension of the crawler.py code written by the memerz-sukay
team for pa2. Modified to crawl and scrape recipes from allrecipes.com, as well
as handle the recipe-related information.

Written by: Melissa Merz
'''

import re
import bs4
import sys
import unicodedata
import pandas as pd

sys.path.append("../")
import url_util


#units to extract from the ingredient strings
UNIT_LIST = ['cup', 'tablespoon', 'teaspoon', 'ounce', 'oz', 'lb', 'pound', \
        'pint', 'clove', 'leaf', 'quart', 'gallon', 'gram', 'g', 'ml', \
        'milliliter', 'fl. ounce', 'tsp', 'tbsp', 'T', 't', 'can', 'package', \
        'slice', 'sprig', 'bunch', 'packet', 'container', 'cups', 'tablespoons', \
        'teaspoons', 'ounces','lbs', 'pounds', 'pints', 'cloves', 'leaves', \
        'quarts', 'gallons', 'grams', 'g', 'ml', 'milliliters', 'fl. ounces', \
        'fluid ounces',' cans', 'packages', 'slices', 'sprigs', 'bunches', \
        'packets', 'containers', 'dash', 'pinch', 'dashes', 'pinches', 'box', \
        'bulb', 'sheet', 'sheets', 'bottle', 'bottles', 'jar', 'jars']

#any recipes with the following categories will not be added to the recipe csvs
BAD_CATS = ["Dessert", "Drink", "Smoothie", "Bread", "Desserts", "Candy", \
        "Cookie", "Cookies", "Drinks", "Candies", "Breads", "Smoothies", "Pie", \
        "Pies", "Sauce", "Sauces", "Condiment", "Condiments", "Dip", "Dips"]


#modified from pa2 code
def get_urls(url, queue_list, visited, links, limiting_domain):
    '''
    Finds all valid urls on current page and adds them to the queue in-place.

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

                if ok and absolute_link not in (visited + queue_list):
                    queue_list.append(absolute_link)


def get_ingredient(ingredient_string):
    '''
    Splits up the ingredient_string into its components -- the amount of the
    ingredient, the units the recipe calls for (like cups or tablespoons), and
    the name of the ingredient.

    Input:
        ingredient_string (str): string containing the ingredient information

    Outputs:
        ingredient (str): name of the ingredient
        amount (float): numerical piece of the total measured amount of the
                ingreident called for by the recipe
        unit (str): unit piece of the total measured amount of the ingredient
                called for by the recipe
    '''
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

        search = re.search(r"\(\d*\.?\d+(\sfluid)? (ounce|pound)\)", \
                ingredient)
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

    ingredient.strip(" ")
    return ingredient, amount, units


#modified from pa2 code
def add_to_csvs(ingredients, categories, image, title, rec_num, link, \
        servings, times, n_reviews, avg_review, ingred_filename, \
        ingred_code_filename, cat_filename, main_filename):
    '''
    Pulls the relevant info out of each tag object and adds it to the index csvs

    Inputs:
        ingredients (dict): dictionary with the unique ingredient codes as keys,
                and the whole, unparsed ingredient string as values
        categories (list of str): list of categories pulled from the recipe html
        image (str): url to the "recommended" or "lead" photo
        title (str): name of the recipe
        link (str): url of the recipe itself
        servings (int): base number of servings which the recipe makes
        times (list of int): list containing the prep time, cook time, and
                total times for the recipe
        n_reviews (int): total number of reviews the recipe has been given
        avg_review (float): avg score out of 5 given to the recipe by users
                who have made the recipe
        ingred_filename (str): filename of the csv containing the ingredient
                information for each recipe
        ingred_code_filename (str): filename of the csv containing the
                unique ingredient codes and their corresponding ingredient names
        cat_filename (str): filename of the csv containing the categories for
                each recipe
        main_filename (str): filename of the csv containing the main information
                for each recipe

    Outputs:
        Adds current page's info to each of the relevant csvs in-place
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

        #if this ingredient is already in the csv, but the name is longer than
        #the name in this recipe (chicken breast vs chicken breast,
        #cut into 1-inch cubes), overwrites the name with the shorter so as to
        #make the record linkage more accurate later on
        elif len(i_codes.loc[code, 'name']) > len(ingredient):
            i_codes.loc[code, 'name'] = ingredient
        ingred_csv.write("\n{}|{}|{}|{}".format(rec_num, amount, units, code))

    for category in categories:
        cat_csv.write("\n{}|{}".format(rec_num, category))

    main_csv.write("\n{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(rec_num, title, \
            link, image, servings, times[0], times[1], times[2], n_reviews, \
            avg_review))

    main_csv.close()
    ingred_csv.close()
    cat_csv.close()
    i_codes.to_csv(ingred_code_filename, index_label = "ingredient_id", \
            sep = "|", mode = "w")


def generate_csvs(main_filename, ingred_filename, ingred_index_filename, \
        cat_filename):
    '''
    Creates the 4 output csvs, overwriting any previously-written files by the
    input file names.

    Inputs:
        main_filename (str): filename of the csv containing the main information
                for each recipe
        ingred_filename (str): filename of the csv containing the ingredient
                information for each recipe
        ingred_code_filename (str): filename of the csv containing the
                unique ingredient codes and their corresponding ingredient names
        cat_filename (str): filename of the csv containing the categories for
                each recipe

    Outputs:
        4 csvs seeded with column headers
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


def get_time(times_list, units_list):
    '''
    Returns the time given a list of time amounts and associated units

    Inputs:
        times_list (list of str): list of numerical strings containing the
                amount of each time unit
        units_list (list of str): list of strings containing each time unit
                for the corresponding amounts

    Output:
        time (int): total time in minutes
    '''
    time = 0
    for i, value in enumerate(times_list):
        if units_list[i].lower() in ["weeks", "week", "wks", "wk", "w"]:
            time += int(value) * 7 * 24 * 60

        elif units_list[i].lower() in ["days", "day", "d"]:
            time += int(value) * 24 * 60

        elif units_list[i].lower() in ["hrs", "hr", "h", "hour", "hours"]:
            time += int(value) * 60

        else:
            time += int(value)

    return time


#modified from pa2 code
def parse_tags(tags):
    '''
    Strips the needed information from the list of potential tags. There are two
    possible types of recipe pages, so methods for extracting the necessary
    info are included for both types.

    Input:
        tags (bs4 result set object): list-like object containing all the
                necessary tags (like 'a' and 'div') on the current page

    Outputs:
        links (list of bs4 tag objects): list containing all 'a' tags
                from parsedhtml
        ingredients (dict): dictionary with the unique ingredient codes as keys,
                and the whole, unparsed ingredient string as values
        image (str): url to the "recommended" or "lead" photo
        title (str): name of the recipe
        categories (list of str): list of categories pulled from the recipe html
        times (list of int): list containing the prep time, cook time, and
                total times for the recipe
        servings (int): base number of servings which the recipe makes
        n_reviews (int): total number of reviews the recipe has been given
        avg_review (float): avg score out of 5 given to the recipe by users
                who have made the recipe
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
    for tag in tags:
        if tag.name == 'a':
            links.append(tag)

        #checks if tag is in the type 1 ingredient format
        elif tag.name == 'label' and tag.has_attr("ng-class") and \
                "{true: 'checkList__item'}[true]" in tag["ng-class"]:
            ingredients[tag.next_element.next_element["data-id"]] = tag["title"]

        #checks if tag is in the type 2 ingredient format
        elif tag.name == 'label' and tag.has_attr("class") and \
                "checkbox-list" in tag["class"]:
            parent = tag.find_parent()
            if parent.has_attr("data-id"):
                ingredients[int(tag.find_parent()["data-id"])] = \
                        tag.findChild("span", {"class": \
                        "ingredients-item-name"}).text.strip()

        #checks if tag is in the type 1 image format
        elif tag.name == "img" and not image and tag.has_attr("class") and \
                "rec-photo" in tag["class"]:
            image = tag["src"]

        #checks if tag is in the type 2 image format
        elif tag.name == "div" and not image and tag.has_attr("class") and\
                "lead-media" in tag["class"]:
            image = tag["data-src"]

        elif tag.name == "title" and not title:
            title = tag.text.split(" Recipe - Allrecipes.com")[0]

        #checks if tag is in the type 1 categories format
        elif tag.name == 'script':
            search = re.search(r"var RdpInferredTastePrefs = \[.+\]", tag.text)
            if search:
                cats = (re.findall("\"\w+\s?\w*\"", search.group()))
                for cat in cats:
                    categories.append(cat.strip("\""))

        #checks if tag is in the type 2 categories format
        elif tag.name == 'div' and tag.has_attr("class") and \
                "keyvals" in tag["class"]:
                    categories.extend(tag["data-content_cms_tags"].split("|"))
                    categories.extend(tag["data-content_cms_category"].split(","))

        #checks if tag is in the type 1 time format
        elif tag.name == "time":
            time_regex = r"\d+"
            unit_regex = r"[a-zA-z]+"
            times_list = re.findall(time_regex, tag["datetime"])
            units_list = re.findall(unit_regex, tag["datetime"])[1:]

            time = get_time(times_list, units_list)

            if tag["itemprop"] == "prepTime":
                times[0] = time

            elif tag["itemprop"] == "cookTime":
                times[1] = time

            else:
                times[2] = time

        #checks if tag is in the type 1 servings format
        elif tag.name == "meta" and tag.has_attr("id") and tag["id"] == \
                "metaRecipeServings":
            servings = int(tag["content"])

        #checks if tag is in the type 2 time or servings format
        elif tag.name == 'div' and tag.has_attr("class") and \
                "recipe-meta-item-header" in tag["class"]:
            text = tag.text.strip()
            if text in ["prep:", "cook:", "total:"]:
                substrings = tag.fetchNextSiblings()[0].text.strip().split(" ")

                times_list = []
                units_list = []
                for s in substrings:
                    if s.isalpha():
                        units_list.append(s)
                    else:
                        times_list.append(s)

                time = get_time(times_list, units_list)

                if text == "prep:":
                    times[0] = time

                elif text == "cook:":
                    times[1] = time

                else:
                    times[2] = time

            elif text == "Servings:":
                servings = int(tag.fetchNextSiblings()[0].text.strip())

        #checks if tag is in the type 1 ratings format
        elif tag.name == "span" and tag.has_attr("itemprop") and \
                tag["itemprop"] == "aggregateRating":
            children = tag.findChildren()
            for child in children:
                if child["itemprop"] == "ratingValue":
                    avg_review = float(child["content"])

                elif child["itemprop"] == "reviewCount":
                    n_reviews = int(child["content"])

        #checks if tag is in the type 2 ratings format
        elif tag.name == "div" and tag.has_attr("class") and \
                "recipe-reviews" in tag["class"]:
            if tag.has_attr("data-ratings-count") and tag["data-ratings-count"] \
                    and tag.has_attr("data-ratings-average") and \
                    tag["data-ratings-average"]:
                n_reviews = int(tag["data-ratings-count"])
                avg_review = float(tag["data-ratings-average"])

    return links, ingredients, image, title, categories, times, servings, \
            n_reviews, avg_review


#modified from pa2 code
def go(num_recipes_to_scrape, ingred_filename, ingred_code_filename, \
        cat_filename, main_filename):
    '''
    Crawl allrecipes.com and generate several csv files with the infomation
    scraped from recipe pages. Recipe pages come in two types, most seem to be
    type 1, but there are a fair number of type 2 as well, so methods are
    included to scrape them both.

    Inputs:
        num_pages_to_crawl (int): the number of pages to process
            during the crawl
        ingred_filename (str): filename of the csv containing the ingredient
                information for each recipe
        ingred_code_filename (str): filename of the csv containing the
                unique ingredient codes and their corresponding ingredient names
        cat_filename (str): filename of the csv containing the categories for
                each recipe
        main_filename (str): filename of the csv containing the main information
                for each recipe

    Outputs:
        4 csv files containing all of the relevant information for each recipe
    '''
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

                #collects tags required for the crawler and csvs
                soup = bs4.BeautifulSoup(request_html, "html5lib")
                #have to collect all tags for both type 1 and type 2 recipes,
                #as they are hard to distinguish efficiently
                tags = soup.find_all({"a": True, "label": True,
                        "script": True, "div": True, "time": True, "meta": True, \
                        "span": True, "img": True, "title": True})
                links, ingredients, image, title, categories, times, servings, \
                        n_reviews, avg_review = parse_tags(tags)

                if n_reviews >= 15 and avg_review >= 3.5 and categories:
                    rec_num = re.search(r"\d+", request_url).group()

                    #checks to make sure the recipe doesn't have any bad
                    #categories, to try and mitigate non-meal foods like
                    #desserts and drinks entering the database
                    add_recipe = True
                    for cat in BAD_CATS:
                        if cat in categories:
                            add_recipe = False
                            break

                    #adds current page info to the index if it's a recipe page
                    if add_recipe:
                        add_to_csvs(ingredients, categories, image, title, \
                                rec_num, request_url, servings, times, n_reviews, \
                                avg_review, ingred_filename, \
                                ingred_code_filename, cat_filename, \
                                main_filename)

                        n_recipes += 1
                        print("Recipe {} added: {}".format(n_recipes, title))
                        print("")

                #queues up all valid urls on current page and prints progress
                get_urls(request_url, queue_list, visited, links, \
                        limiting_domain)
                print("Visited: {}/{} urls at {}".format(len(visited), \
                        len(queue_list + visited), request_url))


#modified from pa2 code
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
