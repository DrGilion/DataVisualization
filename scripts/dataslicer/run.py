import  collections


import Slicer
slicer = Slicer.Slicer("/tmp/dl/complete.json", "/tmp/vis_data/")
slicer.generate_data()
