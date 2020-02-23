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
    fails..
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


hpp_url0 = "https://www.mercato.com/shop/products/hyde-park-produce?offset="
hpp_url1 =  "&ajax=true&productCategoryId=&resetFilters=false&national" +\
            "Shipping=false&deliveryOrPickup=true"


with open("hpp_products.txt", 'w') as txtfile:
    txtfile.write("#Product| PricePerQuant| Quant| PricePerThing \n")
    txtfile.close()

strings_to_remove =  ["C&amp;W ", "&amp"]
list_of_units = [' Pound', ' LB', ' Count', ' Pint',' lb', ' Gallon', \
    ' oz', ' oz.', ' Pounds', ' Quart', ' ct',  ' Liter', ' Liters', ' Gallons', \
    ' Grams',' Ounce', ' Ounces', ' Fluid', ' Pints', ' Milliliters', ' Each',
    ' Jumbo Eggs', ' Large Eggs', ' Extra Large Eggs'] 
undesirableendings = ["-", " ", ",", "."]
remaining = 1
n=0
allproducts = []
while remaining > 0:
    json_url = (hpp_url0 + "{}" + hpp_url1).format(n)
    raw = requests.get(json_url).text
    data = json.loads(raw)
    products = data['products']

    for product in products:                                                                                                                
        productinfo = re.findall("[\t]{6}.*", product)
        nameandquant = (productinfo[0][6:len(productinfo[0])])
        price = (productinfo[2][6:len(productinfo[2])])
        nameandquant = re.sub(r'&amp;', '&', nameandquant)
        price = re.sub(r'&amp;', '&', price) #replace &amp; with &
        for string in strings_to_remove:
            nameandquant = remove_from_string(string, nameandquant)
            price = remove_from_string(string, price)

        nameandquant = remove_from_string("<", nameandquant, "everythingafter")
        nameandquant = remove_from_string(">\n", nameandquant, "everythingbefore")

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
            nameandquant0 = re.sub(r'&amp;', '&', nameandquant0)
            for string in strings_to_remove:
                nameandquant0 = remove_from_string(string, nameandquant0)
            

            nameandquant = re.findall(nameandquant[0:5]+".*", nameandquant0)[0]
            nameandquant = remove_from_string("</h1>]", nameandquant)

        name = ""
        priceperquant = ""
        priceclean = ""
        for unit in list_of_units:
            quants = re.findall("\d*"+unit+"|\d*\.\d*"+unit+"|\d/\d"+unit, nameandquant)
            if quants!=[]:
                a = ""
                for quant in quants:
                    if len(quant) > len(a):
                        a = quant
                quantity = a
                name = remove_from_string(quantity, nameandquant)
                name = remove_from_string(" - ", name)
        for unit in ['/lb', '/LB', " per lb", " per LB"]:
            priceperquantlist = re.findall("\$\d*\.\d*"+unit, price)
            if priceperquantlist !=[]:
                priceperquant = priceperquantlist[0]
                if unit == " per lb" or unit == " per LB":
                    list0 = re.split(" per ", priceperquant)
                    priceperquant = list0[0] + "/" + list0[1]

        for unwanted in [' each', ' each.']:
            pricecleanlist = re.findall("\$\d*\.\d*"+unwanted, price)
            if len(pricecleanlist) > 0:
                priceclean = pricecleanlist[0]
                #sometimes there is a ) following each, we want to remove that
                if unwanted == ' each.':
                    priceclean = priceclean[0:(len(priceclean)-1)]

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

        allproducts.append(productlist)
  
        with open("hpp_products.txt", 'a') as txtfile:
            txtfile.write(str(productlist[0])+ "| " +str(productlist[1])+ "| "+\
                str(productlist[2])+ "| "+str(productlist[3]) + " \n")
            txtfile.close()

    remaining = data['remaining']
    n = len(allproducts)
    print(remaining)
