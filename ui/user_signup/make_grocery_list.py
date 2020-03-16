'''
Functions for generating the grocery list for a given input of ingredients and
for estimating the price for the recipes in a given week.

Written by: Melissa Merz
'''
import pint
import math
import user_signup.search_hpp_products as shp


#to hopefully cut down on conversions, set the default unit system to US imperial
UREG = pint.UnitRegistry(system = "US")

#standard measurement units which pint recognizes
VALID_UNITS = ["cup", "gallon", "tablespoon", "teaspoon", "pint", "quart", \
        "ounce", "fluid_ounce", "pound"]

#units corresponding to tiny weights -- will be equated to 0.01 ounces per unit
TINY_UNITS = ["dash", "dashe", "leaf", "leave", "pinch", "pinche"]

#units corresponding to small weights -- will be equated to 0.15 ounces per unit
SMALL_UNITS = ["bulb", "clove", "packet", "sheet", "sprig"]

#units corresponding to medium weights -- will be equated to 1 ounce per unit
MEDIUM_UNITS = ["slice", "bunch", "bunche", "packet", "stick"]

#units corresponding to large weights -- will be equated to 10 ounces per unit
LARGE_UNITS = ["loaf", "box", "package"]


def convert_mass_to_volume(mass):
    '''
    Converts a mass or weight "mass" to a volume using the density of water as
    a rough estimate for the density of the ingredient.

    Input:
        mass (pint Quantity object): mass or weight of the ingredient in any
                valid units (like pounds, ounces, or grams)

    Output:
        volume (pint Quantity object): volume of the ingredient in cm**3
    '''
    density = UREG("1g / cm**3")
    volume = (mass/density).to_reduced_units()

    return volume


def make_grocery_list(ingredient_list):
    '''
    Makes a grocery list given an input list of ingredients "ingredient_list" by
    consolidating like ingredients into single entries.

    Input:
        ingredient_list (list of tuples): list of ingredient tuples containing
                the number of servings of the recipe it's from, the numerical
                amount required, the units the recipe calls for it in (like
                cups or tablespoons), and the name of the ingredient

    Output:
        ingredients (dict): dictionary with the names of ingredients as the
                keys and dictionaries with the servings, amounts, and units
                as the values

    '''
    ingredients = {}

    for ingredient in ingredient_list:
        servings = ingredient[0]
        amount = ingredient[1]
        unit = ingredient[2]
        name = ingredient[3]
        recipe_num = ingredient[4]

        if str(amount) == 'nan' and unit != "None":
            amount = 1

        elif unit in TINY_UNITS:
            amount *= 0.01
            unit = "ounce"

        elif unit in SMALL_UNITS:
            amount *= 0.15
            unit = "ounce"

        elif unit in MEDIUM_UNITS:
            unit = "ounce"

        elif unit in LARGE_UNITS:
            amount *= 10
            unit = "ounce"

        elif unit not in VALID_UNITS:
            unit = "None"

        if name not in ingredients.keys() or \
                str(ingredients[name]["amount"]) == "nan":
            ingredients[name] = {"servings": servings, "amount": amount, \
                    "unit": unit, "recipe_num" : recipe_num}

        elif ingredients[name]["unit"] == unit:
            ingredients[name]["amount"] += amount
            ingredients[name]["servings"] += servings

        elif ingredients[name]["unit"] == "None" or unit == "None":
            #no good way to convert between an item with no units and an item
            #with units, so we'll assume the one with units is better or more
            #useful for calculating price, so we use the number of servings of
            #each to find the total number required
            ing_servings = ingredients[name]["servings"]

            if unit == "None":
                ing_amount = ingredients[name]["amount"]
                amount_per_serving = ing_amount / ing_servings
                total_servings = ing_servings + servings

            else:
                amount_per_serving = amount / servings
                total_servings = ing_servings + servings
                ingredients[name]["unit"] = unit

            total_amount = total_servings * amount_per_serving

            ingredients[name]["amount"] = total_amount
            ingredients[name]["servings"] = total_servings

        else:
            ing_amount = ingredients[name]["amount"]
            ing_unit = ingredients[name]["unit"]

            quant1 = UREG(str(ing_amount) + ing_unit)
            quant2 = UREG(str(amount) + unit)

            if quant1.dimensionality != quant2.dimensionality:
                if quant1.dimensionality == {'[mass]': 1.0}:
                    quant1 = convert_mass_to_volume(quant1)

                elif quant2.dimensionality == {'[mass]': 1.0}:
                    quant2 = convert_mass_to_volume(quant2)

            ingredients[name]["amount"] = (quant1 + quant2).magnitude

    return ingredients


def estimate_grocery_price(grocery_list):
    '''
    Takes in the output dictionary from the make_grocery_list function and
    interfaces with the database of Hyde Park Produce products through
    search_hpp_products.py to estimate the price of the recipes for the week.

    Input:
        grocery_list (dict: dictionary with the names of ingredients as the
                keys and dictionaries with the servings, amounts, and units
                as the values

    Output:
        (tuple): tuple containing the so-called "raw price", or the price per
                serving for the whole week, based only on how much of each item
                is used (so if a can of beans is needed, but only 50% is used
                for the recipe, it would only add 50% of the price of the can
                to the "raw price"), and the "total price", or the total cost
                assuming that the base number of servings of each recipe is
                made, and that the user is purchasing the whole quantities of
                each (so if a can of beans is needed, but only 50% is used for
                the recipe, it would add the full price to the "total price")
    '''
    raw_price = 0
    total_price = 0

    for item in grocery_list:
        amount = grocery_list[item]["amount"]
        unit = grocery_list[item]["unit"]
        rec_servings = grocery_list[item]["servings"]

        if unit in VALID_UNITS:
            g_quant = UREG(str(amount) + " " + unit)

        elif unit == "fluid ounce" or unit == "fluidounce":
            g_quant = UREG(str(amount) + " fluid_ounce")

        elif unit in TINY_UNITS:
            g_quant = UREG(str(amount * 0.01) + " ounce")

        elif unit in SMALL_UNITS:
            g_quant = UREG(str(amount * 0.15) + " ounce")

        elif unit in MEDIUM_UNITS:
            g_quant = UREG(str(amount) + " ounce")

        elif not unit:
            g_quant = UREG(str(amount) + " dimensionless")

        else:
            g_quant = UREG("1 dimensionless")

        product = shp.find_product(item)

        if product:
            name, price_per_pound, quantity, price = product

            split = quantity.split()
            if len(split) > 1 and split[1] == "fluid":
                quantity = split[0] + " fluid_ounce"
        else:
            name = "None"
            price_per_pound = "None"
            quantity = "None"
            price = "None"

        #these items are bought by the pound instead of in fixed
        #amounts, so the raw price is the same as the total price (per serving)
        if price_per_pound != "None":
            if g_quant.dimensionality == {'[mass]': 1.0}:
                s_quant = UREG('1 pound')
                raw_amount = (g_quant / s_quant).to_reduced_units().magnitude

            elif g_quant.dimensionality == {'[length]': 3.0}:
                s_vol = convert_mass_to_volume(UREG('1 pound'))
                raw_amount = (g_quant / s_vol).to_reduced_units().magnitude

            else:
                #not enough information to determine how much to buy, so we have
                #to assume one pound is enough
                raw_amount = 1

            item_price = float(price_per_pound) * raw_amount
            raw_price += item_price / rec_servings
            total_price += item_price

        elif price != "None":
            if quantity != "None" and len(quantity.split()) > 1:
                try:
                    s_quant = UREG(quantity)

                except:
                    s_quant = UREG(str(quantity) + " dimensionless")

            else:
                s_quant = UREG("1 dimensionless")

            if g_quant.dimensionality == s_quant.dimensionality:
                raw_amount = (g_quant / s_quant).to_reduced_units().magnitude

            elif g_quant.dimensionality == {'[length]': 3.0} and \
                    s_quant.dimensionality == {'[mass]': 1.0}:
                s_vol = convert_mass_to_volume(s_quant)
                raw_amount = (g_quant / s_vol).to_reduced_units().magnitude

            elif g_quant.dimensionality == {'[mass]': 1.0} and \
                    s_quant.dimensionality == {'[length]': 3.0}:
                g_vol = convert_mass_to_volume(s_quant)
                raw_amount = (s_quant / g_vol).to_reduced_units().magnitude

            else:
                #not enough information to determine how much to buy, so we have
                #to assume one unit's worth is enough
                raw_amount = 1

            raw_price += float(price) * raw_amount / rec_servings
            total_amount = math.ceil(raw_amount)
            total_price += float(price) * total_amount

    return (round(raw_price, 2), round(total_price, 2))
