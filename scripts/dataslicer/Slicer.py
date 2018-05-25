import json, collections

class Slicer:
    def __init__(self, dump_file, output_dir='data/'):
        self.dump_file = dump_file
        self.output_dir = output_dir

        self.data = None

    def init(self):
        if not self.data:
            with open(self.dump_file, 'r') as f:
                self.data = json.load(f)

    def set_json_file(self, name, data):
        file = '%s%s.json' % (self.output_dir, name)
        with open(file, 'w') as f:
            f.write(json.dumps(data))

    def gen_cats_file(self):
        pass

    def gen_cc_file(self):
        pass

    def slice_country_products_partners(self):
        self.init()

        for c in self.data:
            cc = c["cc"]

            all_products = set(c["data"]["import"].keys())
            all_products.update(c["data"]["export"].keys())

            for product in all_products:
                imports = c["data"]["import"].get(product, {})
                exports = c["data"]["export"].get(product, {})

                all_years = set(imports.keys())
                all_years.update(exports.keys())

                for year in all_years:
                    y_imports = imports.get(year, {})
                    y_exports = exports.get(year, {})

                    file = "partners_%(country)s_%(year)s_%(product)s" % {
                        "country":cc.lower(),
                        "year":year,
                        "product":product.lower()
                    }
                    
                    data = {
                        "imports": [
                            {"cc":cc, "amount":y_imports[cc]}
                            for cc in y_imports.keys()
                        ],
                        "exports": [
                            {"cc": cc, "amount": y_exports[cc]}
                            for cc in y_exports.keys()
                        ]
                    }

                    self.set_json_file(file, data)

    def slice_country_aggregates(self):
        self.init()

        for c in self.data:
            years = collections.defaultdict(lambda: {"import": {}, "export": {}})

            cc = c["cc"]
            for type in c["data"].keys():
                y_products = collections.defaultdict(lambda : {})

                for product in c["data"][type].keys():
                    if product.lower() == "total":
                        continue

                    for year in c["data"][type][product].keys():
                        stats = c["data"][type][product][year]
                        total_usd = sum([stats[cc] for cc in stats.keys() if cc.lower() != "wld"])
                        y_products[year][product] = total_usd

                # relative werte
                for year in y_products.keys():
                    total_usd = sum([y_products[year][k] for k in y_products[year].keys() if k.lower() != "total"])
                    for prod in y_products[year].keys():
                        v = y_products[year][prod]
                        y_products[year][prod] = (v/total_usd)*100

                    years[year][type] = y_products[year]

            # in ausgabeformat wandeln
            op_data = {
                "years": []
            }

            for year in years.keys():
                op_data["years"].append({
                    "year": year,
                    "imports":[
                        {"id":product_id, "percent": round(percent,3)}
                        for product_id, percent in years[year]["import"].items()
                    ],
                    "exports":[
                        {"id": product_id, "percent": round(percent,3)}
                        for product_id, percent in years[year]["export"].items()
                    ]
                })

            self.set_json_file("aggregate_%s" % cc.lower(), op_data)

    def generate_data(self):
        self.slice_country_products_partners()
        self.slice_country_aggregates()

