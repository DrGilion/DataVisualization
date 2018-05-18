import json, logging, sys, console, urllib, time
from ext import urlfetch

def cc_list():
    with open('cc.txt') as f:
	    content = f.readlines()
    return [c.split(' ')[0] for c in content]

def cc_dict():
    with open('cc.txt') as f:
	    content = f.read().splitlines()
    ccl = [c.split(' ', 1) for c in content]
    ccd = {}
    for cc in ccl:
        ccd[cc[0]] = cc[1].strip()
    return ccd

def set_json_file(name, data):
    file = 'data/%s.json' % name
    with open(file, 'w') as f:
        f.write(json.dumps(data))


def get_retry(url, retries=3):
    for i in range(0, retries):
        try:
            return urlfetch.get(url)
        except:
            time.sleep(1)
    raise Exception("Could not perform urlfetch.get(%s)" % url)

def get_ei_data(cc, indicator, partner_cc="all"):
    url = "http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/%s/year/all/partner/%s/indicator/%s?format=JSON" % (
        cc.lower(),
        partner_cc.lower(),
        indicator.upper()
    )

    try:
        response = urlfetch.get(url)
        if response.status != 200:
            response.close()
            raise Exception("Invalid Status Code: %s (cc: %s)" % (response.status, cc))
        response.text

        # reset if no data exists. -.-
    except (ConnectionResetError, urlfetch.UrlfetchException):
        response = get_retry(url.replace("?format=JSON", ""))
        response.close()

        if response.status != 404:
            raise Exception("Connection Failure")
        return None
    
    data = json.loads(response.text)
    response.close()
    return data

def get_partner_data(base_cc, partner_cc, indicator="XPRT-TRD-VL"):
    url = "http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/%s/year/all/partner/%s/product/all/indicator/%s?format=JSON" % (
        base_cc.lower(),
        partner_cc.lower(),
        indicator.upper()
    )

    try:
        response = urlfetch.get(url)
        if response.status != 200:
            response.close()
            raise Exception("Invalid Status Code: base_country=%s, partner_country=%s" % (base_cc, partner_cc))
        response.text

        # reset if no data exists. -.-
    except (ConnectionResetError, urlfetch.UrlfetchException):
        response = get_retry(url.replace("?format=JSON", ""))
        response.close()
        if response.status != 404:
            raise Exception("Connection Failure")
        return None

    data = json.loads(response.text)
    response.close()
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

    if not yearly_export_cats or not yearly_import_cats:
        return response
    
    # parse raw data
    yearly_export_cats = extract_cats_years(yearly_export_cats)
    yearly_import_cats = extract_cats_years(yearly_import_cats)

    years_s = set(yearly_export_cats.keys())
    years_s = years_s.union(yearly_import_cats.keys())

    for year in years_s:
        response["years"].append({
            "year": year,
            "imports": yearly_import_cats.get(year, []),
            "exports": yearly_export_cats.get(year, [])
        })

    return response

#####################################################
def generate_yearly_aggregates():
    ccs = cc_list()
    ccs_len = len(ccs)

    for i in range(0, ccs_len):
        console.printProgressBar(i, ccs_len)

        cc = ccs[i]
        data = get_cc_aggregates_data(cc)
        name = "aggregate_%s" % cc.lower()
        set_json_file(name, data)

    print("Data has been downloaded!")


def generate_cc_list():
    dct = cc_dict()
    set_json_file("cc_list", dct)
    print("CC List has been generated!")


def main():
    while True:
        opt = console.select_option("Select which Data you want to download", [
            {"id": "yagg", "desc": "Yearly aggregates for every Country"},
            {"id": "ccli", "desc": "Country Codes List"}
        ])

        if opt == "yagg":
            generate_yearly_aggregates()
        
        if opt == "ccli":
            generate_cc_list()

        input("Press Enter to continue")

main()
#d = get_import_data("USA")
#print extract_cc_set(d)
#print len(cc_list())