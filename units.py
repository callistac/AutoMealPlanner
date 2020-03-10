import csv
import re

with open('hpp_products.') as csvfile:
	products = csv.reader(csvfile, delimiter='|')

	possible_units = []
	possible_ppq = []
	for row in products:
		priceperquants = re.findall("[a-zA-Z]*", row[1])
		units = re.findall("[a-zA-Z]*\s[a-zA-Z]*", row[2])
		for ppq in priceperquants:
			if ppq not in possible_ppq:
				possible_ppq.append(ppq)
		for unit in units:
			if unit not in possible_units:
				possible_units.append(unit)
				
	print(possible_units)
	print(possible_ppq)

