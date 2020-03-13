"""
CMSC Winter '20
Grocery JSON Webscrapping Step
Sources:
For learning how to conviently access the data in the infinite scroll
https://ianlondon.github.io/blog/web-scraping-discovering-hidden-apis/
"""
import requests
import json
import re
import csv
import bs4
import url_util as util
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

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

#hyde park produce json file link
hpp_url0 = "https://www.mercato.com/shop/products/hyde-park-produce?offset="
hpp_url1 =  "&ajax=true&productCategoryId=&resetFilters=false&national" +\
            "Shipping=false&deliveryOrPickup=true"

#All the units lists were generated with HPP_unit_scrapper
strings_to_remove =  ["C&amp;W ", "&amp"]

list_of_units = [' Count', ' Pound', ' LB', ' Pint',' lb', ' Gallon', ' oz', 
                ' oz.', ' Pounds', ' Quart',  ' Liter', ' Liters', ' Gallons',
                ' Grams',' Ounce', ' Ounces', ' Fluid Ounces', ' Pints', 
                ' Milliliters', ' ct', ' Each', ' Jumbo Eggs', ' Large Eggs', 
                ' Extra Large Eggs', ' Pack'] 
units_to_remove = [' ct', ' Each', ' Count', ' Extra Large Eggs',
                    ' Jumbo Eggs', ' Large Eggs', 'Pack']
units_to_convert = {" LB":" Pound", " lb":" pound", 
                    " Fluid Ounces":" fluid_ounces", "oz": " oz"}
undesirableendings = ["-", " ", ",", "."]

with open("hpp_products.csv", 'w') as csvfile:
    csvfile.write("Product|PricePerPound|Quant|PricePerThing\n")
    csvfile.close()

remaining = 1 #products left to find, this number will update in the while loop
n = 0 #product we are currently on, used when we have to fetch new json
while remaining > 0:
    json_url = (hpp_url0 + "{}" + hpp_url1).format(n)
    raw = requests.get(json_url).text
    data = json.loads(raw)
    products = data['products']

    for product in products:                                                                                                             
        productinfo = re.findall("[\t]{6}.*", product)
        nameandquant = (productinfo[0][6:len(productinfo[0])])
        price = (productinfo[2][6:len(productinfo[2])])

        nameandquant = remove_from_string("<", nameandquant, "everythingafter")
        nameandquant = remove_from_string(">\n", nameandquant, 
                                                "everythingbefore")
        price = remove_from_string("<", price, "everythingafter")

        #If the name was too long to have in the preview json, it will end
        #with "...". Get the link to the product page and get the full name.
        checkiffulltitle = re.findall(".*\.\.\.", nameandquant)
        if checkiffulltitle != []:
            product_url = re.findall("https://www.*", product)[0]
            request = util.get_request(product_url[0:-1]) 
            #get_request(...) ends with " since it was a string in the json, 
            #we have to remove that or it will go to an error page.
            request_html = util.read_request(request)
            soup = bs4.BeautifulSoup(request_html, "html.parser")
            nameandquant0 = str(soup.find_all("h1",
                class_="product-detail-info__main-text"))
        
            nameandquant = re.findall(nameandquant[0:5]+".*", nameandquant0)[0]
            nameandquant = remove_from_string("</h1>]", nameandquant)

        #replace &amp; with &
        nameandquant = re.sub(r'&amp;', '&', nameandquant)
        for string in strings_to_remove:
            nameandquant = remove_from_string(string, nameandquant)
            price = remove_from_string(string, price)

        name = ""
        #extract name and quantity from namandquant
        for unit in list_of_units:
            quants = re.findall("\d*"+unit+"|\d*\.\d*"+unit+"|\d/\d"+unit,
                                    nameandquant)
            if quants!=[]:
                foundquant = ""
                for quant in quants:
                    if len(quant) > len(foundquant):
                        foundquant = quant
                quantity = foundquant

                #remove the quantituy from the name
                name = remove_from_string(quantity, nameandquant)
                name = remove_from_string(" - ", name)

                #clean up the quanitity; get rid units pint doesn't recognize,
                #make sure all units are lowercase, not empty strings, etc.
                for unit in units_to_remove:
                    quantity = remove_from_string(unit, quantity)

                quantunit = re.findall("\w*\s+\w*|\w+", quantity)
                if quantunit:
                    if quantunit[0] in units_to_convert:
                        new_unit = units_to_convert[quantunit[0]]
                        quantity = remove_from_string(quantunit[0], quantity) \
                                        + new_unit

                quantity = quantity.lower()

                if quantity == "":
                    quantity = None

        priceperquant = ""
        #remove the quanity from priceperquant, since it is always pounds
        for unit in ['/lb', '/LB', " per lb", " per LB"]:
            priceperquantlist = re.findall("\$\d*\.\d*"+unit, price)
            if priceperquantlist !=[]:
                priceperquant = re.findall("\d*\.\d*", priceperquantlist[0])[0]

        if name:
            while name[len(name)-1] in undesirableendings:
                name = name[0:(len(name)-1)]
        else:
            while nameandquant[len(nameandquant)-1] in undesirableendings:
                nameandquant = nameandquant[0:(len(nameandquant)-1)]

        #remove dollar sign, each if it there, and random spaces from price
        price = re.findall("\d*\.\d*", price)[0]

        #save to productlist depending on what info we scrapped
        if name != "" and priceperquant != "":
            productlist = [name, priceperquant, quantity, None]
        elif name != "":
            productlist = [name, None, quantity, price]
        elif priceperquant != "":
            productlist = [nameandquant, priceperquant, None, None]
        else:
            productlist = [nameandquant, None, None, price]

        with open("hpp_products.csv", 'a') as csvfile:
            csvfile.write(str(productlist[0])+ "|" +str(productlist[1])+ "|"+\
                str(productlist[2])+ "|"+str(productlist[3]) + "\n")
            csvfile.close()

        n += 1 #increment the number of products looked at

    remaining = data['remaining']
    print("remaining items: " + str(remaining))
