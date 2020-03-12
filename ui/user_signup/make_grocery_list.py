'''

'''
import pint
import math
import search_hpp_products as shp

UREG = pint.UnitRegistry(system = "US")

#measurement units which pint will recognize
VALID_UNITS = ["cup", "gallon", "tablespoon", "teaspoon", "pint", "quart", \
        "ounce", "fluid ounce", "fluid_ounce", "pound", "fluidounce"]

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

    '''
    density = UREG("1g / cm**3")

    return (mass/density).to_reduced_units()


def make_grocery_list(ingredient_list):
    '''

    '''
    ingredients = {}

    for ingredient in ingredient_list:
        servings = ingredient[0]
        amount = ingredient[1]
        unit = ingredient[2]
        name = ingredient[3]
        if unit in TINY_UNITS:
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

        if name not in ingredients.keys():
            ingredients[name] = {"servings": servings, "amount": amount, \
                    "unit": unit}

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

    '''
    raw_price = 0
    total_price = 0

    for item in grocery_list:
        amount = grocery_list[item]["amount"]
        unit = grocery_list[item]["unit"]
        rec_servings = grocery_list[item]["servings"]

        if unit in VALID_UNITS:
            g_quant = UREG(str(amount) + unit)

        elif unit == "fluid ounce" or unit == "fluidounce":
            g_quant = UREG(str(amount) + "fluid_ounce")

        elif unit in TINY_UNITS:
            g_quant = UREG(str(amount * 0.01) + "ounce")

        elif unit in SMALL_UNITS:
            g_quant = UREG(str(amount * 0.15) + "ounce")

        elif unit in MEDIUM_UNITS:
            g_quant = UREG(str(amount) + "ounce")

        elif not unit:
            g_quant = UREG(str(amount) + " dimensionless")

        else:
            g_quant = UREG("1 dimensionless")

        product = shp.find_product(item)

        if product:
            name, price_per_pound, quantity, price = product
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
            if quantity != "None":
                try:
                    s_quant = UREG(quantity)

                except:
                    s_quant = UREG(str(quantity) + "dimensionless")

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
