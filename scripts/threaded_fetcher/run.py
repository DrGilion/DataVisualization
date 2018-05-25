import time, misc
from ImportMaster import ImportMaster

clear = lambda: print("\033[H\033[J")
master = ImportMaster("ressources/cc.txt")
master.start()

while master.is_alive():
    clear()
    print(master.get_status_string())
    time.sleep(2)

results = master.get_results()
misc.set_json_file("complete", results)
