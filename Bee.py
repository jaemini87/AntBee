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
	def func_EV(self,EV,result_EV):
		for ii in range(0,4):
			for jj in range(0,4):
				i = ii
				j = jj
				if ii == 3 :
					i = 100
				if jj == 3:
					j = 100
				if EV[0] > 0.1-i*0.1 and EV[2] > 0.1-j*0.1:
					result_EV[(ii*4)+jj]+=1
					return result_EV
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
	def analysis_votes(self):
		conn = sql.connect(self.db_file)
		cur = []
		result = []
		for ii in range(0,13):
			cur.append(conn.cursor())
			result.append(0)
		cur[0].execute("select * from MLB_V1")
		result = [0.0,0.0,0.0,0.0]
		EV = [0.0,0.0,0.0,0.0]
		result_EV = [[0 for N in range(0,16)] for M in range(0,7)]
		NN = 0
		for fetch in reversed(cur[0].fetchall()) :
			NN += 1
			print fetch
			if NN == 10:
				break
			EV[0] = fetch[16]/(fetch[15]+fetch[16])-fetch[31]/100.0
			EV[1] = fetch[15]/(fetch[15]+fetch[16])-fetch[32]/100.0
			EV[2] = fetch[18]/(fetch[17]+fetch[18])-fetch[33]/100.0
			EV[3] = fetch[17]/(fetch[17]+fetch[18])-fetch[34]/100.0
			if fetch[10] == 1 and fetch[14] == -1:
				result_EV[0] = self.func_EV(EV,result_EV[0])
			if fetch[12] == 1 and fetch[14] == -1:
				result_EV[1] = self.func_EV(EV,result_EV[1])
			if fetch[11] == 1 and fetch[14] == -1:
				result_EV[2] = self.func_EV(EV,result_EV[2])
			if fetch[10] == 1 and fetch[14] == 1:
				result_EV[3] = self.func_EV(EV,result_EV[3])
			if fetch[11] == 1 and fetch[14] == 1:
				result_EV[4] = self.func_EV(EV,result_EV[4])
			if fetch[13] == 1:
				result_EV[5] = self.func_EV(EV,result_EV[5])
			if fetch[12] == 1:
				result_EV[6] = self.func_EV(EV,result_EV[6])
			"""
			if abs(EV[0]) < 0.1:
				if fetch[15] > fetch[16]:
					if fetch[19]+fetch[20] > fetch[24]+fetch[25]:
					#if fetch[8] > fetch[9]:
						result[0] += fetch[15]*1.2-1.0
					else:
						result[0] -= 1.0
				else:
					#if fetch[9]>fetch[8]:
					if fetch[19]+fetch[20] < fetch[24]+fetch[25]:
						result[1] += fetch[16]*1.2-1.0
					else:
						result[1] -= 1.0
			else:
				if fetch[15] < fetch[16]:
					if fetch[19]+fetch[20] > fetch[24]+fetch[25]:
						result[0] += fetch[15]*1.16-1.0
					else:
						result[0] -= 1.0
				else:
					if fetch[19]+fetch[20] < fetch[24]+fetch[25]:
						result[1] += fetch[16]*1.16-1.0
					else:
						result[1] -= 1.0
			if abs(EV[2]) > 0.1:
				if EV[2] < EV[3]:
					if fetch[14] == 1:
						result[2] += fetch[18]-1.0
					else:
						result[2] -= 1
				if EV[3] < EV[2]:
					if fetch[14] == -1:
						result[3] += fetch[17]-1.0
					else:
						result[3] -=1
			"""
			round_EV = [round(N,2) for N in EV]
			round_result = [round(N,2) for N in result]
#			print fetch[6:10],fetch[19]+fetch[20],fetch[24]+fetch[25],fetch[15:19],fetch[31:35],round_EV,round_result
#			print fetch[6:10],fetch[19:21]+fetch[21:23],fetch[24:26]+fetch[26:28],fetch[15:19],fetch[31:35],round_EV,round_result
		for N in range(0,7):
			print result_EV[N]
		print NN
		pass
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




myBee = Bee("V1_usa_mlb-2013.db")
#myBee.analysis_run_over()
myBee.analysis_votes()
