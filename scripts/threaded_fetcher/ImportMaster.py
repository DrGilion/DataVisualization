import threading, ImportWorker, queue, time

class ImportMaster(threading.Thread):
    def __init__(self, cc_file, worker_count=4):
        super(ImportMaster, self).__init__()

        self.cc_file = cc_file
        self.work_queue = queue.Queue()
        self.results_queue = queue.Queue()

        self.workers = []
        for i in range(0, worker_count):
            self.workers.append(ImportWorker.ImportWorker(self.work_queue, self.results_queue))

    def load_ccs(self):
        with open(self.cc_file) as f:
            content = f.read().splitlines()

        ccl = [c.split(' ', 1) for c in content]
        for cco in ccl:
            self.work_queue.put(cco[0])

    def start_workers(self):
        for i in range(0, len(self.workers)):
            self.workers[i].start()

    def allow_workers_to_end(self):
        for i in range(0, len(self.workers)):
            self.workers[i].stop_if_finished()

    def alive_workers(self):
        alive = []
        for worker in self.workers:
            if worker.is_alive():
                alive.append(worker)
        return alive

    def run(self):
        self.load_ccs()
        self.start_workers()
        self.allow_workers_to_end()

        while len(self.alive_workers()) > 0:
            time.sleep(2)

    def get_results(self):
        results = []
        while not self.results_queue.empty():
            try:
                results.append(self.results_queue.get(False))
            except queue.Empty:
                pass
        return results

    def get_status_string(self):
        status_str = []
        status_str.append("-"*10)
        status_str.append("Workers:")
        status_str.append("-"*10)

        i = 0
        for worker in self.workers:
            alive_status = "alive" if worker.is_alive() else "finished"

            status_str.append("Worker #%(worker_id)s (%(alive_status)s): Processed %(items_processed)s items / %(http_requests)s HTTP Requests" % {
                "worker_id": i,
                "alive_status": alive_status,
                "items_processed": worker.processed_items(),
                "http_requests": worker.get_http_requests()
            })
            i += 1

        status_str.append("-" * 10)
        status_str.append("Work Queue: %s" % self.work_queue.qsize())
        status_str.append("Result Queue: %s" % self.results_queue.qsize())
        status_str.append("-" * 10)

        return "\n".join(status_str)