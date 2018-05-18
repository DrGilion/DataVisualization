import json, logging
from ext import urlfetch

def cc_list():
    with open('cc.txt') as f:
	    content = f.readlines()
    return [c.split(' ')[0] for c in content]

def get_ei_data(cc, indicator, partner_cc="all"):
    url = "http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/%s/year/all/partner/%s/indicator/%s?format=JSON" % (
        cc.lower(),
        partner_cc.lower(),
        indicator.upper()
    )
    response = urlfetch.get(url)
    if response.status != 200:
        raise Exception("Invalid Status Code: %s (cc: %s)" % (response.status, cc))

    data = json.loads(response.text)
    return data

def get_partner_data(base_cc, partner_cc, indicator="XPRT-TRD-VL"):
    url = "http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/%s/year/all/partner/%s/product/all/indicator/%s?format=JSON" % (
        base_cc.lower(),
        partner_cc.lower(),
        indicator.upper()
    )
    response = urlfetch.get(url)
    if response.status != 200:
        raise Exception("Invalid Status Code: base_country=%s, partner_country=%s" % (base_cc, partner_cc))

    data = json.loads(response.text)
    return data

def get_export_data(cc):
    return get_ei_data(cc, "XPRT-PRTNR-SHR")

def get_import_data(cc):
    return get_ei_data(cc, "MPRT-PRTNR-SHR")

def get_world_exports_by_categories(cc):
    return get_partner_data(cc, "wld", "XPRT-PRDCT-SHR")

def get_world_imports_by_categories(cc):
    return get_partner_data(cc, "wld", "MPRT-PRDCT-SHR")

def extract_cc_set(ei_data):
    for s in ei_data["structure"]["dimensions"]["series"]:
        if s["id"] == "PARTNER":
            return set([v["id"] for v in s["values"]])
    raise Exception("cc_set has no partners! :(")

def extract_cats_years(ei_data):
    obs = ei_data["structure"]["dimensions"]["observation"][0]
    if obs["id"] != "TIME_PERIOD":
        raise Exception("Excepted TIME_PERIOD got %s" % obs["id"])
    
    year_map = {}
    for i in range(0, len(obs["values"])):
        year_map[i] = int(obs["values"][i]["name"])


    pcode = None
    srs = ei_data["structure"]["dimensions"]["series"]
    for sr in srs:
        if sr["id"] == "PRODUCTCODE":
            pcode = sr
            break

    if not pcode:
        raise Exception("Could not find Productcode Series")

    category_position = pcode["keyPosition"]
    category_map = {}
    for i in range(0, len(pcode["values"])):
        category_map[i] = {
            "id": pcode["values"][i]["id"],
            "name": pcode["values"][i]["name"]
        }

    # daten durchgehen
    # format von response_data:
    # {2001:[{"id":"categoryId", "name":"categoryName", "percent":12.21}]}
    response_data = {}

    if len(ei_data["dataSets"]) > 1:
        raise Exception("Got more dataSets than expected!")

    data = ei_data["dataSets"][0]["series"]
    for k in data.keys():
        k_parts = k.split(":")
        cat_part = k_parts[category_position]
        cat_id = int(cat_part)

        category = category_map[cat_id]
        for year_key in data[k]["observations"].keys():
            year = year_map[int(year_key)]
            percent = data[k]["observations"][year_key][0]

            # in response_data einfuegen
            obj = response_data.get(year, [])
            obj.append({"id":category["id"], "name":category["name"], "percent":percent})
            response_data[year] = obj

    # daten zurueckgeben
    # format [{"year":2001, "categories":[{"id":"categoryId", "name":"categoryName", "percent":12.21}]}]
    #return [{"year":year, "categories":response_data[year]} for year in response_data.keys()]
    return response_data


def get_cc_aggregates_data(cc):
    # response_data
    response = {
        "years":[]
    }

    # get raw data
    yearly_export_cats = get_world_exports_by_categories(cc)
    yearly_import_cats = get_world_imports_by_categories(cc)

    # parse raw data
    yearly_export_cats = extract_cats_years(yearly_export_cats)
    yearly_import_cats = extract_cats_years(yearly_import_cats)

    years_s = set(yearly_export_cats.keys())
    years_s = years_s.union(yearly_import_cats.keys())

    for year in years_s:
        response["years"].append({
            "year": year,
            "imports": yearly_import_cats[year],
            "exports": yearly_export_cats[year]
        })

    return response

def get_country_data(cc):
    yearly_export_categories = get_world_exports_by_categories(cc)
    yearly_import_categories = get_world_imports_by_categories(cc)




    exp_data = get_export_data(cc)
    exp_ccs = extract_cc_set(exp_data)

    imp_data = get_import_data(cc)
    imp_ccs = extract_cc_set(imp_data)

    partner_ccs = exp_ccs.union( imp_css)
    for partner_cc in ccs:
        partner_data = get_partner_data(cc, partner_cc)
        raise Exception("test")

def main():
    pass

#d = get_world_exports_by_categories("usa")
#parsed = extract_cats_years(d)
print(get_cc_aggregates_data("usa"))

#d = get_import_data("USA")
#print extract_cc_set(d)
#print len(cc_list())