import os, sys

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def select_option(title, opts):
    def _m():
        print("-"*36)
        print("%s:" % title)
        for opt in opts:
            print("[%s] %s" % (opt["id"], opt["desc"]))
        print("[exit] Exit Program")
        print("-"*36)
    
    def _clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    _clear()
    while True:
        _m()
        opt = input("Selection: ")
        opt = str(opt).strip()

        if opt not in [opt["id"] for opt in opts] + ["exit"]:
            _clear()
            print("Invalid Input!")
            continue

        if opt == "exit":
            sys.exit()

        return opt