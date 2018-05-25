import requests, collections
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring

indicators = {
    "import" : "MPRT-TRD-VL",
    "export" :"XPRT-TRD-VL"
}

key_prefix = "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message}"

trade_types = [
    "import",
    "export"
]

product_codes = [
    "01-05_Animal",
    "06-15_Vegetable",
    "16-24_FoodProd",
    "25-26_Minerals",
    "27-27_Fuels",
    "28-38_Chemicals",
    "39-40_PlastiRub",
    "41-43_HidesSkin",
    "44-49_Wood",
    "50-63_TextCloth",
    "64-67_Footwear",
    "68-71_StoneGlas",
    "72-83_Metals",
    "84-85_MachElec",
    "86-89_Transport",
    "90-99_Miscellan",
    "AgrRaw",
    "Chemical",
    "Food",
    "Fuels",
    "OresMtls",
    "Textiles",
    "Total",
    "Transp",
    "UNCTAD-SoP1",
    "UNCTAD-SoP2",
    "UNCTAD-SoP3",
    "UNCTAD-SoP4",
    "manuf"
]

def request_data(base_country, type, product="Total"):
    if type not in trade_types:
        raise ValueError("Wrong type")
    if product not in product_codes:
        raise ValueError("Invalid Product Code")

    indicator = indicators[type]
    partner_country = "all"

    url =  ("http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/" + \
            "reporter/%(base_country)s/year/all/partner/%(partner_country)s/"+ \
            "product/%(product)s/indicator/%(indicator)s") % {
        "base_country" : base_country.lower(),
        "partner_country" : partner_country.lower(),
        "product" : product,
        "indicator" : indicator
    }

    req = requests.get(url)
    if req.status_code == 404:
        return None

    if req.status_code != 200:
        raise Exception("HTTP Request failed!\n%s" % url)

    return bf.data(fromstring(req.text))

def __get_list(obj):
    if not isinstance(obj, list):
        return [obj]
    return obj


def get_products_data(data_obj):
    result = {
        """
        "ProductCode": {
            "year": {
                "CountryCode": 123123
            }
        }
        """
    }
    result = collections.defaultdict(lambda : collections.defaultdict(dict))

    data = data_obj["%sStructureSpecificData" % key_prefix]["%sDataSet" % key_prefix]["Series"]

    for obj in __get_list(data):
        country_c = obj["@PARTNER"]
        product_c = obj["@PRODUCTCODE"]
        for y in __get_list(obj["Obs"]):
            year = y["@TIME_PERIOD"]
            volume = y["@OBS_VALUE"]
            result[product_c][year][country_c] = volume

    return  result
