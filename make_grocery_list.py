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
MEDIUM_UNITS = ["slice", "loaf", "bunch", "bunche", "box", "package", "packet"]


def make_grocery_list(ingredient_list):
    '''
    
    '''
    ingredients = {}

    for ingredient in ingredient_list:
        amount = ingredient[0]
        unit = ingredient[1]
        name = ingredient[2]

        if name not in ingredients.keys():
            ingredients[name] = {"amount": amount, "unit": unit}

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

        if unit in VALID_UNITS:
            g_quant = UREG(str(amount) + unit)
            
        elif unit == "fluid ounce" or unit == "fluidounce":
            g_quant = UREG(str(amount) + "fluid_ounce")

        elif unit in TINY_UNITS:
            g_quant = UREG(str(amount * 0.01) + "ounce")

        elif unit in SMALL_UNITS:
            g_quant = UREG(str(amount * 0.15) + "ounce")

        elif unit in MEDIUM_UNITSL
            g_quant = UREG(str(amount) + "ounce")
            
        else:
            g_quant = UREG(str(amount) + "dimensionless")
            
        name, price_per_pound, quantity, price = shp.find_product(item)

        if price_per_pound and g_quant.dimensionality == {'[mass]': 1.0}:
            s_quant = UREG('1 / pound')
            raw_amount = (g_quant * s_quant).to_reduced_units().magnitude
            item_price = round(float(price_per_pound) * raw_amount, 2)

            #since this type of item is bought by the pound instead of in fixed
            #amounts, the raw price is the same as the total price 
            raw_price += item_price
            total_price += item_price

        elif price_per_pound and g_quant.dimensionality == {'[length]': 3.0}:
            s_quant = UREG('1 / pound')

            #it would be difficult or imposible to get an accurate density for
            #each product, so we assume that every product is the density of
            #water so we can find a (relatively) accurate price
            density = UREG("1g / cm**3")
            s_vol = (s_quant/density).to_reduced_units()
            raw_amount = (g_quant * s_vol).to_reduced_units().magnitude
            item_price = round(float(price_per_pound) * raw_amount, 2)
            
            #since this type of item is bought by the pound instead of in fixed
            #amounts, the raw price is the same as the total price 
            raw_price += item_price
            total_price += item_price

            
    return (raw_price, total_price)
