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
        nameandquant = re.sub(r'&amp;', '&', nameandquant)
        price = re.sub(r'&amp;', '&', price) #replace &amp; with &

        nameandquant = remove_from_string("<", nameandquant, "everythingafter")
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
            nameandquant = remove_from_string("<h1 class=" +\
                "\"product-detail-info__main-text\">\n", nameandquant0)
            nameandquant = remove_from_string("</h1>", nameandquant)
            nameandquant = nameandquant[1:(len(nameandquant)-1)] #get rid of []
            
            for string in strings_to_remove:
                nameandquant = remove_from_string(string, nameandquant)
            nameandquant = re.sub(r'&amp;', '&', nameandquant)

        #split up names, quantities, and prices
        priceperquant = re.split("/", price)
        if len(priceperquant) == 2:
            name = remove_from_string("-", nameandquant,
                            "everythingafter")
            priceperquant[0] = remove_from_string("each", priceperquant[0],
                                "everythingbefore")
            priceperquant[0] = priceperquant[0]
            pricequant = priceperquant[0] + " " + priceperquant[1]
            productlist = [name, pricequant[2:(
                                len(pricequant)-1)] , None, None]
        elif len(priceperquant) == 1:
            priceperquant = re.split(" per ", price)
            nameandquantlist= re.split("-", nameandquant)
            #re.split this part
            #sometimes instead of denoting the start of the quantity with a
            #dash, hpp uses a comma, so we must also check for that.
            if len(nameandquantlist) != 2:
                #splits for ", 32 " or ", 1/", as in ", 32 oz." or 
                #", 1/2 gallon". Just ",\s\d" catches "100% pure tea" etc.
                nameandquantlist2= re.split(",\s\d*[\s/]", nameandquant)
                if len(nameandquantlist2) == 2:
                    #put the \d*[\s/] part back in
                    a = re.findall(",\s\d.*", nameandquant)[0]
                    nameandquantlist2[1] = a[2:len(a)]

            price = remove_from_string("each", price, "everythingafter")
            price = re.findall("[\d]*\.[\d]{2}", price)[0] #exclude $ sign

            if len(nameandquantlist) == 2:
                productlist = [nameandquantlist[0], None, nameandquantlist[1],
                    price]
            elif len(nameandquantlist2) == 2: 
                productlist = [nameandquantlist2[0], None, nameandquantlist2[1], 
                    price]
            elif len(priceperquant) == 2:
                productlist = [nameandquantlist[0], priceperquant[0] +\
                    " " + priceperquant[1], None , None] #!!!
            else:
                productlist = [nameandquantlist[0], None, None, price]

        else:
            print("no price for this item" + str(nameandquant))
        allproducts.append(productlist)

        with open("hpp_products.txt", 'a') as txtfile:
            txtfile.write(str(productlist[0])+ "| " +str(productlist[1])+ "| "+\
                str(productlist[2])+ "| "+str(productlist[3]) + " \n")
            txtfile.close()

    remaining = data['remaining']
    n = len(allproducts)
    print(remaining)
