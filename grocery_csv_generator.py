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
import urllib.parse

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
    return urllib.parse.urlparse(url).netloc != ""


hpp_url0 = "https://www.mercato.com/shop/products/hyde-park-produce?offset="
hpp_url1 =  "&ajax=true&productCategoryId=&resetFilters=false&national" +\
            "Shipping=false&deliveryOrPickup=true"

with open("hydeparkproduce.txt", 'w') as txtfile:
    txtfile.write("Product, PricePerQuant, Quant, PricePerThing \n")
    txtfile.close()

strings_to_remove =  ["C&amp;W ", "&amp"]
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

        for string in strings_to_remove:
            nameandquant = remove_from_string(string, nameandquant)
            price = remove_from_string(string, price)
        nameandquant = remove_from_string("<", nameandquant, "everythingafter")
        price = remove_from_string("<", price, "everythingafter")

        checkiffulltitle = re.findall(".*\.\.\.", nameandquant)
        if checkiffulltitle != []:
            product_url = re.findall("https://www.*", product)[0]
            request = get_request(product_url)
            request_html = read_request(request)
            soup = bs4.BeautifulSoup(request_html, "html5lib")
            body = soup.find("body")
            z = body.contents
            for x in z:
                print(x)
                print(" ")
            #print(div2)

        #split up names, quantities, and prices
        priceperquant = re.split("/", price)
        if len(priceperquant) == 2:
            name = remove_from_string("-", nameandquant, 
                            "everythingafter")
            priceperquant[0] = remove_from_string("each", priceperquant[0], 
                                "everythingbefore")
            priceperquant[0] = priceperquant[0]
            pricequant = priceperquant[0] + " " + priceperquant[1]
            productlist = [name, pricequant[2:(len(pricequant
                            )-1)] , None, None]
        elif len(priceperquant) == 1:
            priceperquant = re.split(" per ", price)
            nameandquantlist= re.split("-", nameandquant)
            nameandquantlist2= re.split(", ", nameandquant)
            price = remove_from_string("each", price, "everythingafter")
            if len(nameandquantlist) == 2:
                productlist = [nameandquantlist[0], None, nameandquantlist[1], 
                    price]
            elif len(nameandquantlist2) == 2:
                productlist = [nameandquantlist2[0], None, nameandquantlist2[1], 
                    price]
            elif len(priceperquant) == 2:
                productlist = [priceperquant[0], priceperquant[0][2:(
                    len(pricequant)-1)] , None, None]
            else:
                productlist = [nameandquantlist[0], None, None, price]
        else:
            print("no price for this item" + str(nameandquant))

        allproducts.append(productlist)
        #print(productlist)

        with open("hydeparkproduce.txt", 'a') as csv:
            csv.write(str(productlist) + ' \n')
            csv.close()
    remaining = data['remaining']
    n = len(allproducts)
    print(remaining)
