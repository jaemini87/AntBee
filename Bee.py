__author__ = 'jaemin'
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
class Bee:
	Name = ""
	Budjet = 100.0
	def __init__(self,db_file):
		self.db_file = db_file
	def gen_Ref(self):
		pass
	def gen_Price(self):
		pass
	def analysis(self):
		conn = sql.connect(self.db_file)
		cur = []
		result = []
		for ii in range(0,13):
			cur.append(conn.cursor())
			result.append(0)
		cur[0].execute("select * from MLB_V1")
		#all good betting
		cur[1].execute("select * from MLB_V1 where su=:t1 and ou=:t2",{"t1": 1, "t2": 1})
		cur[2].execute("select * from MLB_V1 where su=:t1 and ou=:t2",{"t1": 1, "t2": -1})
		cur[3].execute("select * from MLB_V1 where su=:t1 and ou=:t2",{"t1": -1, "t2": 1})
		cur[4].execute("select * from MLB_V1 where su=:t1 and ou=:t2",{"t1": -1, "t2": -1})

		#over and run_su
		cur[5].execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": 1, "t2": 1})
		#only these betting is allowed
		cur[6].execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": 1, "t2": -1})
		cur[7].execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": -1, "t2": 1})
		#under and +1 handi
		cur[8].execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": -1, "t2": -1})

		cur[9].execute("select * from MLB_V1 where run_utd=:t1 and ou=:t2",{"t1": 1, "t2": 1})
		cur[10].execute("select * from MLB_V1 where run_utd=:t1 and ou=:t2",{"t1": 1, "t2": -1})
		cur[11].execute("select * from MLB_V1 where run_utd=:t1 and ou=:t2",{"t1": -1, "t2": 1})
		cur[12].execute("select * from MLB_V1 where run_utd=:t1 and ou=:t2",{"t1": -1, "t2": -1})
		for ii in range(0,13):
			for fetch in cur[ii].fetchall():
				#print fetch
				result[ii]+=1
		print result
	def analysis_run_over(self):
		conn = sql.connect(self.db_file)
		cur = conn.cursor()
		#cur.execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": 1, "t2": 1})
		#cur.execute("select * from MLB_V1 where utd=:t1 and ou=:t2",{"t1": 1, "t2": -1})
		cur.execute("select * from MLB_V1 where ou=:t2",{"t2": 1})
		x= []
		y= []
		ii = 1
		arg_num = 8
		arg_amp = 1
		for fetch in cur.fetchall():
			arg_list = fetch
			home_su = arg_amp if (arg_list[15] < arg_list[16]) else -arg_amp
			#y.append(home_su*(arg_list[29+6+arg_num]/(0.000001+arg_list[29+6+11+arg_num])))
			result = home_su*(arg_list[29+6+arg_num]/(0.000001+arg_list[29+6+11+arg_num]))

			print arg_list[35+arg_num],arg_list[46+arg_num],result
			discrete = 0 if abs(1-abs(result)) < 0.1 else (1 if result > 0 else -1)
			y.append(discrete)
			x.append(ii)
			ii+=1
#		x = np.random.randn(1000)
#		y = np.random.randn(1000)
		fig, ax = plt.subplots()

		# histogram our data with numpy
		data = y
		n, bins = np.histogram(data, 200)

		# get the corners of the rectangles for the histogram
		left = np.array(bins[:-1])
		right = np.array(bins[1:])
		bottom = np.zeros(len(left))
		top = bottom + n

		# we need a (numrects x numsides x 2) numpy array for the path helper
		# function to build a compound path
		XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T

		# get the Path object
		barpath = path.Path.make_compound_path_from_polys(XY)

		# make a patch out of it
		patch = patches.PathPatch(
			barpath, facecolor='blue', edgecolor='gray', alpha=0.8)
		ax.add_patch(patch)

		# update the view limits
		ax.set_xlim(left[0], right[-1])
		ax.set_ylim(bottom.min(), top.max())

		plt.show()




myBee = Bee("V1_usa_mlb-2014.db")
myBee.analysis_run_over()