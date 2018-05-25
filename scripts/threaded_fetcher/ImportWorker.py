import threading, queue, Worldbank

class ImportWorker(threading.Thread):
    def __init__(self, input_queue, output_queue):
        super(ImportWorker, self).__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.http_requests = 0
        self.items_processed = 0
        self.stop = False

    def fetch_cc_data(self, cc):
        final_data = {}
        """
            "cc" : "USA",
            "data" : {
                "import" : {
                    "ProductCode": {
                        "year": {
                            "CountryCode": 123123
                        }
                    }
                },
                "export": siehe oben
            }
        """

        final_data["cc"] = cc
        final_data["data"] = {}

        for ttype in Worldbank.trade_types:
            for product in Worldbank.product_codes:
                data = Worldbank.request_data(cc, ttype, product)
                self.http_requests += 1
                if not data:
                    continue

                data = Worldbank.get_products_data(data)
                final_data["data"][ttype] = data

        self.items_processed += 1
        self.output_queue.put(final_data)


    def run(self):
        while True:
            try:
                cc = self.input_queue.get(True, 1)
                self.fetch_cc_data(cc)
            except queue.Empty:
                if self.stop:
                    break

    def stop_if_finished(self):
        self.stop = True

    def processed_items(self):
        return self.items_processed

    def get_http_requests(self):
        return self.http_requests