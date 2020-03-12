"""
Grocery JSON Webscrapping Step
Written by Dylan Sukay
Sources:
For learning how to conviently access the data in the infinite scroll
https://ianlondon.github.io/blog/web-scraping-discovering-hidden-apis/
"""

import requests
import json
import re
import csv
import bs4
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

#from pa2
def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL

    Outputs:
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''

    if is_absolute_url(url):
        try:
            r = requests.get(url)
            if r.status_code == 404 or r.status_code == 403:
                r = None
        except Exception:
            # fail on any kind of error
            r = None
    else:
        r = None

    return r


#from pa2
def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails.
    '''

    try:
        return request.text.encode('iso-8859-1')
    except Exception:
        print("read failed: " + request.url)
        return ""

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

#from pa2
def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if url == "":
        return False
    return urlparse(url).netloc != ""

#hyde park produce json file link
hpp_url0 = "https://www.mercato.com/shop/products/hyde-park-produce?offset="
hpp_url1 =  "&ajax=true&productCategoryId=&resetFilters=false&national" +\
            "Shipping=false&deliveryOrPickup=true"

with open("hpp_products.csv", 'w') as csvfile:
    csvfile.write("Product|PricePerPound|Quant|PricePerThing\n")
    csvfile.close()

strings_to_remove =  ["C&amp;W ", "&amp"]
#All the units lists were generated with HPP_unit_scrapper
strings_to_remove =  ["C&amp;W ", "&amp"]
list_of_units = [' Count', ' Pound', ' LB', ' Pint',' lb', ' Gallon', ' oz', ' oz.', 
                ' Pounds', ' Quart',  ' Liter', ' Liters', ' Gallons',
                ' Grams',' Ounce', ' Ounces', ' Fluid Ounces', ' Pints', ' Milliliters', 
                ' ct', ' Each', ' Jumbo Eggs', ' Large Eggs', 
                ' Extra Large Eggs'] 
units_to_remove = [' ct', ' Each', ' Count', ' Extra Large Eggs',
                    ' Jumbo Eggs', ' Large Eggs']
units_to_convert = {" LB":" Pound", " lb":" pound", 
                    " Fluid Ounces":" fluid_ounces"}
undesirableendings = ["-", " ", ",", "."]

remaining = 1 #products left to find, this number will update in the while loop
n = 0 #product we are currently on
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
            request = get_request(product_url[0:-1]) 
            #get_request(...) ends with " since it was a string in the json, 
            #we have to remove that or it will go to an error page.
            request_html = read_request(request)
            soup = bs4.BeautifulSoup(request_html, "html.parser")
            nameandquant0 = str(soup.find_all("h1",
                class_="product-detail-info__main-text"))
        
            nameandquant = re.findall(nameandquant[0:5]+".*", nameandquant0)[0]
            nameandquant = remove_from_string("</h1>]", nameandquant)

        #replace &amp; with &
        nameandquant = re.sub(r'&amp;', '&', nameandquant)
        price = re.sub(r'&amp;', '&', price)
        for string in strings_to_remove:
            nameandquant = remove_from_string(string, nameandquant)
            price = remove_from_string(string, price)

        name = ""
        priceperquant = ""
        priceclean = ""
        for unit in list_of_units:
            quants = re.findall("\d*"+unit+"|\d*\.\d*"+unit+"|\d/\d"+unit,
                                    nameandquant)
            if quants!=[]:
                foundquant = ""
                for quant in quants:
                    if len(quant) > len(foundquant):
                        foundquant = quant
                quantity = foundquant
                name = remove_from_string(quantity, nameandquant)
                name = remove_from_string(" - ", name)

        for unit in ['/lb', '/LB', " per lb", " per LB"]:
            priceperquantlist = re.findall("\$\d*\.\d*"+unit, price)
            if priceperquantlist !=[]:
                priceperquant = re.findall("\d*\.\d*", priceperquantlist[0])[0]

        pricecleanlist = re.findall("\$\d*\.\d*"+" each", price)
        if len(pricecleanlist) > 0:
            priceclean = re.findall("\$\d*\.\d*" + " each", 
                                        pricecleanlist[0])[0]

        if name != "":
            while name[len(name)-1] in undesirableendings:
                name = name[0:(len(name)-1)]
        else:
            while nameandquant[len(nameandquant)-1] in undesirableendings:
                nameandquant = nameandquant[0:(len(nameandquant)-1)]

        if type(priceclean) == list:
            priceclean = remove_from_string("each", priceclean[0])
        else:
            priceclean = remove_from_string("each", str(priceclean))

        if type(price) == list:
            price = remove_from_string("each", price[0])
        else:
            price = remove_from_string("each", price)

        if name != "" and priceperquant != "":
            productlist = [name, priceperquant, quantity, None]
        elif name != "" and priceclean != "":
            productlist = [name, None, quantity, priceclean]
        elif name != "":
            productlist = [name, None, quantity, price]
        elif priceperquant != "":
            productlist = [nameandquant, priceperquant, None, None]
        elif priceclean != "":
            productlist = [nameandquant, None, None, priceclean]
        else:
            productlist = [nameandquant, None, None, price]

        
        if productlist[1]:
            productlist[1]  = re.findall("\d*\.\d*", productlist[1])[0]

        if productlist[2]:
            for unit in units_to_remove:
                productlist[2] = remove_from_string(unit, productlist[2])
            
            unit = re.findall("\w*\s+\w*|\w+", productlist[2])
            if unit:
                if unit[0] in units_to_convert:
                    new_unit = units_to_convert[unit[0]]
                    productlist[2] = (remove_from_string(unit[0], 
                        productlist[2]) + new_unit)
            productlist[2] = productlist[2].lower()
            if productlist[2] == "":
                productlist[2] = None

        if productlist[3]:
            productlist[3] = re.findall("\d*\.\d*", productlist[3])[0]

        with open("hpp_products.csv", 'a') as csvfile:
            csvfile.write(str(productlist[0])+ "|" +str(productlist[1])+ "|"+\
                str(productlist[2])+ "|"+str(productlist[3]) + "\n")
            csvfile.close()
        n += 1
        productlist = []

    remaining = data['remaining']
    print("remaining items: " + str(remaining))

