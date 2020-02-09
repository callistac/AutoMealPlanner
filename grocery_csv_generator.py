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

def remove_from_string(remove, string, removeposition = ""):
    removeobj = re.search(remove, string)
    if removeobj != None:
        if removeobj.end() == len(string) or removeposition == "everythingafter":
            string = string[:removeobj.start()]
        elif removeposition == "everythingbefore":
            string = string[removeobj.end():]
        elif removeposition == "":
            string = string[:removeobj.start()] + string[removeobj.end():]

    return string

blank_url0 = "https://www.mercato.com/shop/products/hyde-park-produce?offset="

blank_url1 =  "&ajax=true&productCategoryId=&resetFilters=false&national" +\
            "Shipping=false&deliveryOrPickup=true"

with open("hydeparkproduce.txt", 'w') as txtfile:
    txtfile.write("Product, PricePerQuant, Quant, PricePerThing \n")
    txtfile.close()

strings_to_remove =  ["C&amp;W "]
remaining = 1
n=0
allproducts = []
while remaining > 0:
    json_url = (blank_url0 + "{}" + blank_url1).format(n)
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
        print(productlist)

        with open("hydeparkproduce.txt", 'a') as csv:
            csv.write(str(productlist) + ' \n')
            csv.close()
    remaining = data['remaining']
    n = len(allproducts)
    print(remaining)
