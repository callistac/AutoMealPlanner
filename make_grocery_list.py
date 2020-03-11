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
MEDIUM_UNITS = ["slice", "loaf", "bunch", "bunche", "box", "package", "packet", \
        "stick"]


def make_grocery_list(ingredient_list):
    '''

    '''
    ingredients = {}

    for ingredient in ingredient_list:
        servings = ingredient[0]
        amount = ingredient[1]
        unit = ingredient[2]
        name = ingredient[3]

        if name not in ingredients.keys():
            ingredients[name] = {"recipe_servings": servings, "amount": amount, \
                    "unit": unit}

        elif name in ingredients.keys() and ingredients[name]["unit"] == unit:
            ingredients[name]["amount"] += amount

        else:
            ing_amount = ingredients[name]["amount"]
            ing_unit = ingredients[name]["unit"]

            quant1 = UREG(str(ing_amount) + ing_unit)
            quant2 = UREG(str(amount) + unit)

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
        rec_servings = grocery_list[item]["recipe_servings"]

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

        if price_per_pound != "None" and g_quant.dimensionality == \
                {'[mass]': 1.0}:
            s_quant = UREG('1 / pound')
            raw_amount = (g_quant * s_quant).to_reduced_units().magnitude
            item_price = float(price_per_pound) * raw_amount / rec_servings

            #since this type of item is bought by the pound instead of in fixed
            #amounts, the raw price is the same as the total price
            raw_price += item_price
            total_price += item_price

        elif price_per_pound != "None" and g_quant.dimensionality == \
                {'[length]': 3.0}:
            s_quant = UREG('1 / pound')

            #it would be difficult or imposible to get an accurate density for
            #each product, so we assume that every product is the density of
            #water so we can find a (relatively) accurate price
            density = UREG("1g / cm**3")
            s_vol = (s_quant * density).to_reduced_units()
            raw_amount = (s_vol * g_quant).to_reduced_units().magnitude
            item_price = float(price_per_pound) * raw_amount / rec_servings

            #since this type of item is bought by the pound instead of in fixed
            #amounts, the raw price is the same as the total price
            raw_price += item_price
            total_price += item_price

        elif price != "None":
            if quantity != "None":
                try:
                    s_quant = UREG(quantity)

                except:
                    s_quant = float(quantity)
            else:
                s_quant = 1.0

            if type(s_quant) == int or type(s_quant) == float:
                #when we don't have units
                raw_price += float(price)
                total_price += float(price)

            elif g_quant.dimensionality == s_quant.dimensionality:
                raw_amount = (g_quant / s_quant).to_reduced_units().magnitude
                raw_price += float(price) * raw_amount / rec_servings
                total_amount = math.ceil(raw_amount)
                total_price += float(price) * total_amount / rec_servings

            elif g_quant.dimensionality == {'[length]': 3.0} and \
                    s_quant.dimensionality == {'[mass]': 1.0}:
                density = UREG("1g / cm**3")
                s_vol = (density / s_quant).to_reduced_units()
                raw_amount = (s_vol * g_quant).to_reduced_units().magnitude
                raw_price += float(price) * raw_amount / rec_servings
                total_amount = math.ceil(raw_amount)
                total_price += float(price) * total_amount / rec_servings

            elif g_quant.dimensionality == {'[mass]': 1.0} and \
                    s_quant.dimensionality == {'[length]': 3.0}:
                density = UREG("1g / cm**3")
                g_vol = (g_quant / density).to_reduced_units()
                raw_amount = (s_quant / g_vol).to_reduced_units().magnitude
                raw_price += float(price) * raw_amount / rec_servings
                total_amount = math.ceil(raw_amount)
                total_price += float(price) * total_amount / rec_servings

            else:
                raw_price += float(price)
                total_price += float(price)

    return (round(raw_price, 2), round(total_price, 2))
