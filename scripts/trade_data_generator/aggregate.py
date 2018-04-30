import os.path, json
import unicodecsv as csv

translate = {
	#"Congo, Dem. Rep." : "Viet Nam",
	"Korea, Rep." : "Korea, Republic of",
	"Iran, Islamic Rep." : "Iran, Islamic Republic of",
	"Ethiopia(excludes Eritrea)" : "Ethiopia",
	"St. Kitts and Nevis" : "Saint Kitts and Nevis",
	"St. Lucia" : "Saint Lucia",
	"Congo, Rep." : "Congo",
	"Tanzania" : "Tanzania, United Republic of",
	"Moldova" : "Moldova, Republic of",
	"South Sudan" : "Sudan",
	"Macedonia, FYR" : "Macedonia, the former Yugoslav Republic of",
	"Korea, Dem. Rep." : "Korea, Democratic People's Republic of",
	"Hong Kong, China" : "Hong Kong",
	"Egypt, Arab Rep." : "Egypt",
	"Slovak Republic" : "Slovakia",
	"Faeroe Islands" : "Faroe Islands",
	"Congo, Dem. Rep." : "Congo, the Democratic Republic of the",
	"Gambia, The" : "Gambia",
	"Kyrgyz Republic" : "Kyrgyzstan",
	"Lao PDR" : "Lao People's Democratic Republic",
	"Serbia, FR(Serbia/Montenegro)" : "Serbia"
}
def trans(inp):
	return translate.get(inp, inp)

#############################################################################


#############################################################################

cc_rev_index = {}
cc_index = {}
with open('metadata/cc_loc.csv') as f:
	r = csv.DictReader(f)
	for row in r:
		cc_index[row["Alpha-3 code"]] = {
			"Name": row["Country"],
			"Latitude": float(row["Latitude (average)"]),
			"Longitude": float(row["Longitude (average)"])
		}
		cc_rev_index[row["Country"]] = row["Alpha-3 code"]


data = {"cc_index":cc_index, "trade_data": {}, "country_aggr_trade_data": {}}
for key in cc_index.keys():

	partners = {}
	
	
	# Load Export Data
	total_export = 0
	cfile = "files/export.%s.csv" % key
	with open(cfile, 'rb') as f:
		r = csv.DictReader(f)
		for row in r:
			pname = trans(row.get("Partner Name"))
			pcode = cc_rev_index.get(pname)
			if pcode:
				amt = None
				try:
					amt = float(row["Export (US$ Thousand)"])
					amt = amt * 1000
				except ValueError:
					continue
				
				if amt:
					total_export += amt
					
					partners[pcode] = {
						"ExportAmount": amt			
					}
	
	# Load Import Data
	total_import = 0
	cfile = "files/import.%s.csv" % key
	with open(cfile, 'rb') as f:
		r = csv.DictReader(f)
		for row in r:
			pname = trans(row.get("Partner Name"))
			pcode = cc_rev_index.get(pname)
			if pcode:
				amt = None
				try:
					amt = float(row["Import (US$ Thousand)"])
					amt = amt * 1000
				except ValueError:
					continue
				
				if amt:
					total_import += amt
					
					partners[pcode] = {
						"ImportAmount": amt			
					}
			
	
	for pkey in partners.keys():
		pdict = partners[pkey]
		
		if "ExportAmount" not in pdict:
			pdict["ExportAmount"] = 0
		if "ImportAmount" not in pdict:
			pdict["ImportAmount"] = 0
		
		if total_export == 0:
			partners[pkey]["ExportAmountPercentage"] = 0
		else:
			partners[pkey]["ExportAmountPercentage"] = round((pdict["ExportAmount"]/total_export)*100, 2)
		
		if total_import == 0:
			partners[pkey]["ImportAmountPercentage"] = 0
		else:
			partners[pkey]["ImportAmountPercentage"] = round((pdict["ImportAmount"]/total_import)*100, 2)
	
	
	if len(partners.keys()) > 0:
		data["trade_data"][key] = partners
		
	data["country_aggr_trade_data"][key] = {
		"TotalImport": total_import,
		"TotalExport": total_export
	}

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

