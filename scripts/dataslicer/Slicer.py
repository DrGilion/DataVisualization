import json, collections, csv, os

class Slicer:
    def __init__(self, dump_file, output_dir='data/'):
        self.dump_file = dump_file
        self.output_dir = output_dir


        self.data = None

    def init(self):
        if not self.data:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            with open(self.dump_file, 'r') as f:
                self.data = json.load(f)

    def get_valid_categories(self):
        with open('ressources/valid_categories') as f:
            content = f.read().splitlines()

        return [cat.strip().lower() for cat in content]

    def get_ccs(self):
        with open('ressources/cc.txt') as f:
            content = f.read().splitlines()

        ccs = {}
        ccl = [c.split(' ', 1) for c in content]
        for cco in ccl:
            ccs[cco[0]] = cco[1]
            if cco[1].count(",") == 1:
                parts = cco[1].split(',', 1)
                complete = "%(pre)s (%(post)s %(pre)s)" % {
                    "pre" : parts[0].strip(),
                    "post" : parts[1].strip()
                }
                ccs[cco[0]] = complete
        return ccs

    def set_json_file(self, name, data):
        file = '%s%s.json' % (self.output_dir, name)
        with open(file, 'w') as f:
            f.write(json.dumps(data))

    def gen_cats_file(self):
        cats = {}

        valid_categories = self.get_valid_categories()

        with open('ressources/products.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ProductGroup'].lower() in valid_categories:
                    cats[row['ProductGroup']] = row['ProductGroupDescription'].strip()

        self.set_json_file("categories", cats)

    def gen_cc_file(self):
        self.init()

        ccs = self.get_ccs()
        result = {}

        for c in self.data:
            cc = c["cc"]

            all_products = set(c["data"]["import"].keys())
            all_products.update(c["data"]["export"].keys())

            if len(all_products) == 0:
                continue

            result[cc] = {
                "full_name": ccs[cc],
                "years":{}
            }

            for product in all_products:
                imports = c["data"]["import"].get(product, {})
                exports = c["data"]["export"].get(product, {})

                all_years = set(imports.keys())
                all_years.update(exports.keys())
                result[cc]["years"][product] = sorted(list(all_years))

        self.set_json_file("countries", result)


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

        valid_categories = self.get_valid_categories()

        for c in self.data:
            years = collections.defaultdict(lambda: {"import": {}, "export": {}})

            cc = c["cc"]
            for type in c["data"].keys():
                y_products = collections.defaultdict(lambda : {})

                for product in c["data"][type].keys():
                    #if product.lower() == "total":
                    #    continue

                    if product.lower() not in valid_categories:
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
        self.gen_cc_file()
        self.gen_cats_file()

