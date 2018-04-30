import urllib
import xlrd
import unicodecsv as csv
import time
import os

with open('cc.txt') as f:
	content = f.readlines()

ccl = [l.strip().split(' ')[0] for l in content]
for cc in ccl:
	xlf = "files/export.%s.xlxs" % cc
	csf = "files/export.%s.csv" % cc	

	url = "https://wits.worldbank.org/Download.aspx?Reporter=%s&Year=2015&Tradeflow=Export&Type=Partner&Lang=en" % cc
	urllib.urlretrieve(url, filename=xlf)
	
	wb = xlrd.open_workbook(xlf)
	sh = wb.sheet_by_name('Partner')
	
	with open(csf, 'w') as f:
		wr = csv.writer(f, quoting=csv.QUOTE_ALL)
		for rn in range(sh.nrows):
			wr.writerow(sh.row_values(rn))

	os.unlink(xlf)
	print("Downloaded Data for: %s" % cc)
	time.sleep(3)

