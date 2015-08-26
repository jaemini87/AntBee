__author__ = 'cad'
from scipy.stats.stats import pearsonr
import numpy as np
import sqlite3 as sql
class Correlation:
	def __init__(self,db_file="all_usamlb-2014.db"):
		self.db_file = db_file
		pass
	def getCorreation(self):
		conn = sql.connect(self.db_file)
		cur = conn.cursor()
		cur.execute("select * from MLB_SU ORDER BY nid DESC ")
		for ii in cur:
			print ii
		pass
		a = []
		b= []
		pearsonr(a,b)

#	[8:13]
#	[17:]

myCorrelation = Correlation()
myCorrelation.getCorreation()