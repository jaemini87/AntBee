__author__ = 'jaemin'
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
#from scipy.stats.stats import pearsonr
class Bee:
	Name = ""
	Budjet = 100.0
	Db_File = ""
	def __init__(self,db_file):
		self.Db_File = db_file
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
	def generate_stability_(self,param):
		"""
			  odds < 1.6 - 2.5
		1.6 < odds < 1.8 - 1.5
		1.8 < odds < 2.0 +-0.5
		2.0 < odds < 2.4 + 1.5
		2.4 < odds       + 2.5
		Basic Stability	Number = -Full_Diff * Odds * Factor3
		Advanced Stability Number = (2-5_Diff + Odds * Factor1 - Full_Diff)*Factor1 + ....
		Sum of Factor should be 1.0
		1   inn 20%
		2-5 inn 40%
		6-8 inn 30%
		9+  inn 10%
		"""
	#param is the number of the game and home away selection 1: home 0: away

		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V1 where nid=:Nid", \
					{"Nid":param[0]})
		cur_game = cur.fetchone()
		homeaway = param[1]
		if homeaway == 1:
			odds= cur_game[16]/(cur_game[15]+cur_game[16])
			score_diff = cur_game[8]-cur_game[9]
			score_list_diff = np.array(cur_game[19:24])-np.array(cur_game[24:29])
			era = [cur_game[4]]
			score_list_era = np.array(cur_game[19:24])/np.arrayt(era[0:5])
			score_list_offset = np.array(cur_game[24:29])+np.array(cur_game[19:24])
		elif homeaway == 0:
			odds= cur_game[15]/(cur_game[15]+cur_game[16])
			score_diff = cur_game[9]-cur_game[8]
			score_list_diff = np.array(cur_game[24:29])-np.array(cur_game[19:24])
			score_list_offset = np.array(cur_game[24:29])+np.array(cur_game[19:24])
		else:
			return
		odds_factor = self.get_odds_factor(odds)
		score_list_factor = self.get_score_list_factor(score_list_offset)
		Stability_list = (score_list_diff+odds_factor)*score_list_factor
		Stability = sum(Stability_list)
		#print Stability_list,score_list_diff,odds_factor,score_list_factor
		#Stability = sum((score_list_diff-score_diff)*score_list_factor)
		#Stability = sum((score_list_diff+np.array(odds_factor)*score_list_factor)*score_list_factor)
		return Stability_list
	pass
	def get_score_list_factor(self,score_list_offset):
		#return [0.00,0.6,0.4,0.0,0.0]
		if score_list_offset[0] == 0 and score_list_offset[3] == 0 and score_list_offset[4] == 0:
			return [0.05,0.5,0.4,0.05,0.0]
		elif score_list_offset[0] == 0 and score_list_offset[3] == 1 and score_list_offset[4] == 0:
			return [0.05,0.45,0.35,0.15,0.0]
		elif score_list_offset[0] == 0 and score_list_offset[3] == 0 and score_list_offset[4] == 1:
			return [0.05,0.45,0.3,0.05,0.15]
		elif score_list_offset[0] == 0 and score_list_offset[3] == 1 and score_list_offset[4] == 1:
			return [0.05,0.35,0.3,0.15,0.15]
		elif score_list_offset[0] == 1 and score_list_offset[3] == 0 and score_list_offset[4] == 0:
			return [0.15,0.45,0.35,0.05,0.0]
		elif score_list_offset[0] == 1 and score_list_offset[3] == 1 and score_list_offset[4] == 0:
			return [0.15,0.4,0.3,0.15,0.0]
		elif score_list_offset[0] == 1 and score_list_offset[3] == 0 and score_list_offset[4] == 1:
			return [0.15,0.4,0.25,0.05,0.15]
		else:
			return [0.15,0.3,0.25,0.15,0.15]
		pass
	def get_odds_factor(self,odds):
		if odds > 0.67:
			return [-0.5,-2.0,-1.0,-0.15,0.0]
		elif odds > 0.57:
			return [-0.15,-1.25,-0.75,-0.15,0.0]
		elif odds > 0.52:
			return [0.0,-0.5,-0.25,0.0,0.0]
		elif odds < 0.52 and odds > 0.48:
			return [0.0,0.0,0.0,0.0,0.0]
		elif odds < 0.48 and odds > 0.43:
			return [0.0,0.5,0.25,0.0,0.0]
		elif odds < 0.43 and odds > 0.33:
			return [0.15,1.25,0.75,0.15,0.0]
		else:
			return [0.5,2.0,1.0,0.15,0.0]
		pass
	def print_pearsonr(self,total_home,total_away):
		result_h = []
		result_a = []
		for ii in range(0,5):
			x = []
			y = []
			for jj in total_home:
				x.append(jj[1]+jj[2])
				#x.append(jj[[6]])
#				xx.append(jj[0]+jj[1])
				y.append(jj[5])
			#result_h.append(pearsonr(x,y))
			result_h.append(np.corrcoef(x,y))
			x = []
			y = []
			for jj in total_away:
				x.append(jj[1]+jj[2])
				y.append(jj[5])
			result_a.append(np.corrcoef(x,y))
			#result_a.append(pearsonr(x,y))
		print result_h
		print "----------------------------"
		print result_a

		pass
	def generate_stability(self,param):
		#param Format
		#0: game number
		#1: last games
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		hist_home = conn.cursor()
		hist_away = conn.cursor()

	#	cur.execute("select * from MLB_V1 where nid=:Nid",\
	#	{"Nid":param[0]})
		cur.execute("select * from MLB_V1 ")
		ii = 0
		total_home = []
		total_away = []
		for cur_game in cur.fetchall():
			if ii > 100:
				hometeam = cur_game[6]
				awayteam = cur_game[7]
				odds_h = 10.0/cur_game[15]
				odds_a = 10.0/cur_game[16]
		#		print hometeam,awayteam
				hist_home.execute("select * from MLB_V1 where nid>:Nid and\
				(team_h=:Hometeam or team_a=:Hometeam)",{"Nid":cur_game[0],"Hometeam":hometeam})
				hist_away.execute("select * from MLB_V1 where nid>:Nid and \
				(team_h=:Awayteam or team_a=:Awayteam)",{"Nid":cur_game[0],"Awayteam":awayteam})
				hist_home_result = np.array([0.0,0.0,0.0,0.0,0.0])
				hist_away_result = np.array([0.0,0.0,0.0,0.0,0.0])
				new_h = []
				new_a = []
				jj = 0
				kk = 0
				for cur_away in hist_away.fetchall():
					if jj == param[1]:
						break
					hist_away_result += np.array(self.generate_stability_([cur_away[0],0]))
					jj+=1
				for cur_home in hist_home.fetchall():
					if kk == param[1]:
						break
					hist_home_result += np.array(self.generate_stability_([cur_home[0],1]))
					kk+=1
				if cur_game[8] > cur_game[9]:
					odds_a = -1*odds_a
					odds_h = 10.0 - odds_h
				else:
					odds_h = -1*odds_h
					odds_a = 10.0 - odds_a
				new_h = np.append(hist_home_result,odds_h)
				new_a = np.append(hist_away_result,odds_a)
				total_home.append(new_h)
				total_away.append(new_a)
			ii+=1
		#print cur_game
		self.print_pearsonr(total_home,total_away)
		NNN=10
		"""
		for test in hist_home.fetchall():
			print test
			print self.generate_stability_([test[0],1])
			print self.generate_stability_([test[0],0])
			NNN-=1
			if NNN==0:
				break
		"""
#		print hist_home.fetchone()
#		print hist_away.fetchall()
		pass



	def generate_stability_result(self,game_number,game_seeds):
		#Game Seed Format

		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V1")



		pass

	def analysis(self):
		conn = sql.connect(self.Db_File)
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
		conn = sql.connect(self.Db_File)
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
		"""
		for N in range(0,7):
			print result_EV[N]
		print NN
		"""
		pass
	def analysis_run_over(self):
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		#cur.execute("select * from MLB_V1 where run_su=:t1 and ou=:t2",{"t1": 1, "t2": 1})
		#cur.execute("select * from MLB_V1 where utd=:t1 and ou=:t2",{"t1": 1, "t2": -1})
		cur.execute("select * from MLB_V1 where ou=:t2",{"t2": 1})
		x= []
		y= []
		ii = 9
		#arg_num starts from 1-11

		arg_num = 4
		arg_amp = 10
		for fetch in cur.fetchall():
			arg_list = fetch
			#arg_list 15 16 odds_h odds_a
			#arg_list 8 9 score_h score_a
			home_su = arg_amp if (arg_list[15] < arg_list[16]) else -arg_amp
			home_su = (arg_amp-arg_amp/arg_list[16]) if (arg_list[8] < arg_list[9]) else -arg_amp/arg_list[16]
			#y.append(home_su*(arg_list[29+6+arg_num]/(0.000001+arg_list[29+6+11+arg_num])))

			#result = home_su*(arg_list[29+5+arg_num]/(arg_list[29+5+11+arg_num])) if abs(arg_list[34+arg_num])>0.01 and abs(arg_list[45+arg_num])>0.01 else 0.0
			result = home_su*(arg_list[34+arg_num]-(arg_list[45+arg_num])) if abs(arg_list[34+arg_num])>0.01 and abs(arg_list[45+arg_num])>0.01 else 0.0
			result = 1 if arg_list[15] < arg_list[16] and arg_list[8] > arg_list[9] else -1
			print arg_list[34+arg_num],arg_list[44+arg_num],fetch
			discrete = result
			#discrete = 0 if abs(1-abs(result)) < 0.1 else (1 if result > 0 else -1)
			y.append(result)
			x.append(ii)
			ii+=1
#		x = np.random.randn(1000)
#		y = np.random.randn(1000)
		print "AVG",np.average(y),"MED",np.median(y)
		print "SUM",np.sum(y),"Size", len(y)
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
		k = []
		plt.show()




myBee = Bee("V1_usa_mlb-2014.db")
myBee.analysis_run_over()
#myBee.generate_stability([100,3])
#myBee.analysis_votes()
