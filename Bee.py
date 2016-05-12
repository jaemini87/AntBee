__author__ = 'jaemin'
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
#from scipy.stats.stats import pearsonr
import random
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

	def bet_prob(self):
		#retrurn +ev list (fulltime,halftime,full ou,half ou)
		#insert_game = [season,day,month,year,time,team_h,team_a,
		#8:  score_h,score_a,
		#10: score_h_half,score_a_half,
		#12: score_ou,score_ou_half,
		#14: odds_h,odds_a,
		#16: odds_h_half,odds_a_half,
		#18: odds_o,odds_u,
		#20: odds_o_half,odds_u_half]
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V2")
		cum_bet_slip = [0.0 for _ in range(0,4)]
		num_bet_slip = [0.0 for _ in range(0,4)]
		for fin_line in cur.fetchall():
			full_score_ratio = fin_line[15]/(fin_line[14]+fin_line[15])
			full_ou_ratio = fin_line[19]/(fin_line[18]+fin_line[19])
			half_score_ratio = fin_line[17]/(fin_line[17]+fin_line[16])
			half_ou_ratio = fin_line[21]/(fin_line[21]+fin_line[20])
			full_score_win = 1 if fin_line[8]>fin_line[9] else -1
			full_ou_win= 1 if fin_line[8]+fin_line[9]>fin_line[12] else (0 if fin_line[8]+fin_line[9]-fin_line[12]<0.1 else -1)
			half_score_win = 1 if fin_line[10]>fin_line[11] else -1
			half_ou_win = 1 if fin_line[11]+fin_line[10]>fin_line[13] else (0 if fin_line[10]+fin_line[11]-fin_line[13]<0.1 else -1)
			bet_slip = []
			rand_list = [[] for ii in range(0,4)]
			for rand in range(0,10):
				if random.random() < full_score_ratio:
					rand_list[0].append(1)
				else:
					rand_list[0].append(0)
				if random.random() < full_ou_ratio:
					rand_list[1].append(1)
				else:
					rand_list[1].append(0)
				if random.random() < half_score_ratio:
					rand_list[2].append(1)
				else:
					rand_list[2].append(0)
				if random.random() < half_ou_ratio:
					rand_list[3].append(1)
				else:
					rand_list[3].append(0)
			if sum(rand_list[0])>5 :
				if 	full_score_win == 1:
					bet_slip.append(fin_line[14]-1.0)
				else:
					bet_slip.append(-1.0)
			elif sum(rand_list[0])<5 :
				if 	full_score_win == -1:
					bet_slip.append(fin_line[15]-1.0)
				else:
					bet_slip.append(-1.0)
			else:
				bet_slip.append(0.0)
			if sum(rand_list[1])>5 :
				if 	full_ou_win == 1:
					bet_slip.append(fin_line[18]-1.0)
				elif full_ou_win == -1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			elif sum(rand_list[1])<5 :
				if 	full_ou_win == -1:
					bet_slip.append(fin_line[19]-1.0)
				elif full_ou_win == 1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			else:
				bet_slip.append(0.0)
			if sum(rand_list[2])>5 :
				if 	half_score_win == 1:
					bet_slip.append(fin_line[16]-1.0)
				elif half_score_win == -1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			elif sum(rand_list[2])<5 :
				if 	half_score_win == -1:
					bet_slip.append(fin_line[17]-1.0)
				elif half_score_win == 1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			else:
				bet_slip.append(0.0)
			if sum(rand_list[3])>5 :
				if 	half_ou_win == 1:
					bet_slip.append(fin_line[20]-1.0)
				elif half_ou_win == -1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			elif sum(rand_list[3])<5 :
				if 	half_ou_win == -1:
					bet_slip.append(fin_line[21]-1.0)
				elif half_ou_win == 1:
					bet_slip.append(-1.0)
				else:
					bet_slip.append(0.0)
			else:
				bet_slip.append(0.0)
			cum_bet_slip += np.array(bet_slip)
			num_bet_slip += np.array(bet_slip)/(np.array(bet_slip)-0.0000001)
		print cum_bet_slip
		print num_bet_slip
		pass

	def generate_stability_result(self,game_number,game_seeds):
		#Game Seed Format

		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V1")
		pass
	def stats_handi(self):
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V2")
	#insert_game = [season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_half,score_a_half,score_ou,score_ou_half,odds_h,odds_a,odds_h_half,odds_a_half,odds_o,odds_u,odds_o_half,odds_u_half]
		#30% under
		#45% under
		#45~50%
		#50~55%
		#55% over
		#70% over
		games = [[0 for ii in range(0,5)] for jj in range(0,12)]
		ev = [[0 for ii in range(0,5)] for jj in range(0,12)]

		for fetch in cur.fetchall():
			win_ratio_h = fetch[15]/(fetch[14]+fetch[15])
			win_ratio_a = fetch[14]/(fetch[14]+fetch[15])
			score_diff = fetch[8]-fetch[9]
			odds_h = fetch[14]
			odds_a = fetch[15]
			if win_ratio_h < 0.35:
				i = 0
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.45:
				i = 1
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.5:
				i = 2
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.55:
				i = 3
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.65:
				i = 4
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			else:
				i = 5
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			win_ratio_h = fetch[14]/(fetch[14]+fetch[15])
			odds_h = fetch[15]
			score_diff = fetch[9]-fetch[8]
			if win_ratio_h < 0.35:
				i = 6
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.45:
				i = 7
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.5:
				i = 8
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.55:
				i = 9
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			elif win_ratio_h < 0.65:
				i = 10
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
			else:
				i = 11
				if score_diff > 2.5:
					games[i][0] += 1
					ev[i][0] += odds_h*1.75-1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 1.5:
					games[i][1] += 1
					ev[i][0] -= 1.0
					ev[i][1] += odds_h*1.4-1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > 0:
					games[i][2] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] += odds_h-1.0
					ev[i][3] += odds_h/1.4-1.0
				elif score_diff > -1.5:
					games[i][3] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] += odds_h/1.4-1.0
				else:
					games[i][4] += 1
					ev[i][0] -= 1.0
					ev[i][1] -= 1.0
					ev[i][2] -= 1.0
					ev[i][3] -= 1.0
		np.set_printoptions(precision=2,suppress=True)
		iter = 0
		print "-----------------HOME-GAMES------------------"
		for kk in games:
			if iter == 6:
				print "-----------------AWAY-GAMES------------------"
			print kk
			iter += 1
		iter = 0
		print "-----------------HOME-EV-------------------"
		for kk in np.array(ev):
			if iter == 6:
				print "-----------------AWAY-EV-------------------"
			print kk
			iter += 1
		print "------------PROB-HOME-GAMES------------------"
		iter = 0
		for kk in games:
			if iter == 6:
				print "------------PROB-AWAY-EV-------------------"
			print np.array([float(kk[0])/sum(kk[0:3]),float(kk[0]+kk[1])/sum(kk[0:3]),float(sum(kk[0:4]))/sum(kk[0:5])])
			iter += 1
		pass

	def stats_ou(self):
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V2")
		#insert_game = [season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_half,score_a_half,score_ou,score_ou_half,odds_h,odds_a,odds_h_half,odds_a_half,odds_o,odds_u,odds_o_half,odds_u_half]
		#odds_h 14
		#odds_a 15
		#score_h 8
		#score_a 9
		games = [0 for ii in range(0,10)]
		games_n = [0 for ii in range(0,10)]
		games_m = [0 for ii in range(0,10)]
		ev = [0.0 for ii in range(0,10)]
		ev_n = [0.0 for ii in range(0,10)]
		ev_m = [0.0 for ii in range(0,10)]
		prob = [0.0 for ii in range(0,8)]
		prob_m = [0.0 for ii in range(0,8)]
		prob_n = [0.0 for ii in range(0,8)]
		night = 0
		morning = 0

		for fetch in cur.fetchall():
			if fetch[5] > 22 or fetch[5] < 7:
				ou = fetch[8]+fetch[9]
				ou_half = fetch[10]+fetch[11]
				score_ou = fetch[12]
				score_ou_half = fetch[13]
				if ou > score_ou+0.1 and ou_half > score_ou_half+0.1:
					games_n[0]+=1
					ev_n[0] += fetch[18]-1.0
					ev_n[1] += fetch[20]-1.0
					ev_n[2] -= 1.0
					ev_n[3] -= 1.0
					pass
				elif ou > score_ou+0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_n[0] += fetch[18]-1.0
					ev_n[1] += 0.0
					ev_n[2] -= 1.0
					ev_n[3] -= 0.0
					games_n[1]+=1
					pass
				elif ou > score_ou+0.1 and ou_half < score_ou_half-0.1:
					ev_n[0] += fetch[18]-1.0
					ev_n[1] -= 1.0
					ev_n[2] -= 1.0
					ev_n[3] += fetch[21]-1.0
					games_n[2]+=1
					pass
				elif abs(ou -score_ou)<0.1 and ou_half > score_ou_half+0.1:
					ev_n[0] += 0.0
					ev_n[1] += fetch[20]-1.0
					ev_n[2] -= 0.0
					ev_n[3] -= 1.0
					games_n[3]+=1
					pass
				elif abs(ou -score_ou)<0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_n[0] += 0.0
					ev_n[1] += 0.0
					ev_n[2] -= 0.0
					ev_n[3] -= 0.0
					games_n[4]+=1
					pass
				elif abs(ou -score_ou)<0.1 and ou_half < score_ou_half-0.1:
					ev_n[0] += 0.0
					ev_n[1] += -1.0
					ev_n[2] -= 0.0
					ev_n[3] += fetch[21]-1.0
					games_n[5]+=1
					pass
				elif ou < score_ou-0.1 and ou_half > score_ou_half+0.1:
					ev_n[0] += -1.0
					ev_n[1] += fetch[20]-1.0
					ev_n[2] += fetch[19]-1.0
					ev_n[3] -= 1.0
					games_n[6]+=1
					pass
				elif ou < score_ou-0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_n[0] += -1.0
					ev_n[1] += 0.0
					ev_n[2] += fetch[19]-1.0
					ev_n[3] -= 0.0
					games_n[7]+=1
					pass
				elif ou < score_ou-0.1 and ou_half < score_ou_half-0.1:
					ev_n[0] += -1.0
					ev_n[1] += -1.0
					ev_n[2] += fetch[19]-1.0
					ev_n[3] += fetch[21]-1.0
					games_n[8]+=1
					pass
				else:
					ev_n[0] += fetch[18]-1.0
					ev_n[1] += fetch[20]-1.0
					ev_n[2] -= 1.0
					ev_n[3] -= 1.0
					games_n[9]+=1
					pass
			else:
				ou = fetch[8]+fetch[9]
				ou_half = fetch[10]+fetch[11]
				score_ou = fetch[12]
				score_ou_half = fetch[13]
				if ou > score_ou+0.1 and ou_half > score_ou_half+0.1:
					games_m[0]+=1
					ev_m[0] += fetch[18]-1.0
					ev_m[1] += fetch[20]-1.0
					ev_m[2] -= 1.0
					ev_m[3] -= 1.0
					pass
				elif ou > score_ou+0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_m[0] += fetch[18]-1.0
					ev_m[1] += 0.0
					ev_m[2] -= 1.0
					ev_m[3] -= 0.0
					games_m[1]+=1
					pass
				elif ou > score_ou+0.1 and ou_half < score_ou_half-0.1:
					ev_m[0] += fetch[18]-1.0
					ev_m[1] -= 1.0
					ev_m[2] -= 1.0
					ev_m[3] += fetch[21]-1.0
					games_m[2]+=1
					pass
				elif abs(ou -score_ou)<0.1 and ou_half > score_ou_half+0.1:
					ev_m[0] += 0.0
					ev_m[1] += fetch[20]-1.0
					ev_m[2] -= 0.0
					ev_m[3] -= 1.0
					games_m[3]+=1
					pass
				elif abs(ou -score_ou)<0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_m[0] += 0.0
					ev_m[1] += 0.0
					ev_m[2] -= 0.0
					ev_m[3] -= 0.0
					games_m[4]+=1
					pass
				elif abs(ou -score_ou)<0.1 and ou_half < score_ou_half-0.1:
					ev_m[0] += 0.0
					ev_m[1] += -1.0
					ev_m[2] -= 0.0
					ev_m[3] += fetch[21]-1.0
					games_m[5]+=1
					pass
				elif ou < score_ou-0.1 and ou_half > score_ou_half+0.1:
					ev_m[0] += -1.0
					ev_m[1] += fetch[20]-1.0
					ev_m[2] += fetch[19]-1.0
					ev_m[3] -= 1.0
					games_m[6]+=1
					pass
				elif ou < score_ou-0.1 and abs(ou_half-score_ou_half) < 0.1:
					ev_m[0] += -1.0
					ev_m[1] += 0.0
					ev_m[2] += fetch[19]-1.0
					ev_m[3] -= 0.0
					games_m[7]+=1
					pass
				elif ou < score_ou-0.1 and ou_half < score_ou_half-0.1:
					ev_m[0] += -1.0
					ev_m[1] += -1.0
					ev_m[2] += fetch[19]-1.0
					ev_m[3] += fetch[21]-1.0
					games_m[8]+=1
					pass
				else:
					ev_m[0] += fetch[18]-1.0
					ev_m[1] += fetch[20]-1.0
					ev_m[2] -= 1.0
					ev_m[3] -= 1.0
					games_m[9]+=1
					pass
			ou = fetch[8]+fetch[9]
			ou_half = fetch[10]+fetch[11]
			score_ou = fetch[12]
			score_ou_half = fetch[13]
			if ou > score_ou+0.1 and ou_half > score_ou_half+0.1:
				games[0]+=1
				ev[0] += fetch[18]-1.0
				ev[1] += fetch[20]-1.0
				ev[2] -= 1.0
				ev[3] -= 1.0
				pass
			elif ou > score_ou+0.1 and abs(ou_half-score_ou_half) < 0.1:
				ev[0] += fetch[18]-1.0
				ev[1] += 0.0
				ev[2] -= 1.0
				ev[3] -= 0.0
				games[1]+=1
				pass
			elif ou > score_ou+0.1 and ou_half < score_ou_half-0.1:
				ev[0] += fetch[18]-1.0
				ev[1] -= 1.0
				ev[2] -= 1.0
				ev[3] += fetch[21]-1.0
				games[2]+=1
				pass
			elif abs(ou -score_ou)<0.1 and ou_half > score_ou_half+0.1:
				ev[0] += 0.0
				ev[1] += fetch[20]-1.0
				ev[2] -= 0.0
				ev[3] -= 1.0
				games[3]+=1
				pass
			elif abs(ou -score_ou)<0.1 and abs(ou_half-score_ou_half) < 0.1:
				ev[0] += 0.0
				ev[1] += 0.0
				ev[2] -= 0.0
				ev[3] -= 0.0
				games[4]+=1
				pass
			elif abs(ou -score_ou)<0.1 and ou_half < score_ou_half-0.1:
				ev[0] += 0.0
				ev[1] += -1.0
				ev[2] -= 0.0
				ev[3] += fetch[21]-1.0
				games[5]+=1
				pass
			elif ou < score_ou-0.1 and ou_half > score_ou_half+0.1:
				ev[0] += -1.0
				ev[1] += fetch[20]-1.0
				ev[2] += fetch[19]-1.0
				ev[3] -= 1.0
				games[6]+=1
				pass
			elif ou < score_ou-0.1 and abs(ou_half-score_ou_half) < 0.1:
				ev[0] += -1.0
				ev[1] += 0.0
				ev[2] += fetch[19]-1.0
				ev[3] -= 0.0
				games[7]+=1
				pass
			elif ou < score_ou-0.1 and ou_half < score_ou_half-0.1:
				ev[0] += -1.0
				ev[1] += -1.0
				ev[2] += fetch[19]-1.0
				ev[3] += fetch[21]-1.0
				games[8]+=1
				pass
			else:
				ev[0] += fetch[18]-1.0
				ev[1] += fetch[20]-1.0
				ev[2] -= 1.0
				ev[3] -= 1.0
				games[9]+=1
				pass

		over = sum(games_n[0:6])
		over_h = games_n[0]+games_n[1]+games_n[3]+games_n[4]+games_n[6]+games_n[7]
		under = sum(games_n[3:10])
		under_h = games_n[2]+games_n[1]+games_n[5]+games_n[4]+games_n[7]+games_n[8]
		prob_n[0] = float(games_n[0]+games_n[1]+games_n[3]+games_n[4])/over
		prob_n[1] = float(games_n[0]+games_n[1]+games_n[3]+games_n[4])/over_h
		prob_n[2] = float(games_n[7]+games_n[8]+games_n[5]+games_n[4])/under
		prob_n[3] = float(games_n[7]+games_n[8]+games_n[5]+games_n[4])/under_h

		prob_n[4] = float(games_n[2]+games_n[1]+games_n[5]+games_n[4])/over # fulltime is over but half inn is under bullpen bad
		prob_n[5] = float(games_n[7]+games_n[6]+games_n[3]+games_n[4])/over_h # halftime is over but full inn under bullpen good

		prob_n[6] = float(games_n[7]+games_n[6]+games_n[3]+games_n[4])/under # fulltime is under but halftime over bullpen good
		prob_n[7] = float(games_n[2]+games_n[1]+games_n[5]+games_n[4])/under_h # halftime is under but fulltime over bullpen bad

		over = sum(games_m[0:6])
		over_h = games_m[0]+games_m[1]+games_m[3]+games_m[4]+games_m[6]+games_m[7]
		under = sum(games_m[3:10])
		under_h = games_m[2]+games_m[1]+games_m[5]+games_m[4]+games_m[7]+games_m[8]
		prob_m[0] = float(games_m[0]+games_m[1]+games_m[3]+games_m[4])/over
		prob_m[1] = float(games_m[0]+games_m[1]+games_m[3]+games_m[4])/over_h
		prob_m[2] = float(games_m[7]+games_m[8]+games_m[5]+games_m[4])/under
		prob_m[3] = float(games_m[7]+games_m[8]+games_m[5]+games_m[4])/under_h

		prob_m[4] = float(games_m[2]+games_m[1]+games_m[5]+games_m[4])/over # fulltime is over but half inn is under bullpen bad
		prob_m[5] = float(games_m[7]+games_m[6]+games_m[3]+games_m[4])/over_h # halftime is over but full inn under bullpen good

		prob_m[6] = float(games_m[7]+games_m[6]+games_m[3]+games_m[4])/under # fulltime is under but halftime over bullpen good
		prob_m[7] = float(games_m[2]+games_m[1]+games_m[5]+games_m[4])/under_h # halftime is under but fulltime over bullpen bad

		over = sum(games[0:6])
		over_h = games[0]+games[1]+games[3]+games[4]+games[6]+games[7]
		under = sum(games[3:10])
		under_h = games[2]+games[1]+games[5]+games[4]+games[7]+games[8]
		prob[0] = float(games[0]+games[1]+games[3]+games[4])/over
		prob[1] = float(games[0]+games[1]+games[3]+games[4])/over_h
		prob[2] = float(games[7]+games[8]+games[5]+games[4])/under
		prob[3] = float(games[7]+games[8]+games[5]+games[4])/under_h

		prob[4] = float(games[2]+games[1]+games[5]+games[4])/over # fulltime is over but half inn is under bullpen bad
		prob[5] = float(games[7]+games[6]+games[3]+games[4])/over_h # halftime is over but full inn under bullpen good

		prob[6] = float(games[7]+games[6]+games[3]+games[4])/under # fulltime is under but halftime over bullpen good
		prob[7] = float(games[2]+games[1]+games[5]+games[4])/under_h # halftime is under but fulltime over bullpen bad
		#It is more likely happen pro
		print "-------------------------------------START-------------------------------"
		print games
		print games_n
		print games_m
		print "-------------------------------------------------------------------------"
		print prob
		print prob_n
		print prob_m
		print "-------------------------------------------------------------------------"
		print ev
		print ev_n
		print ev_m
		print "------------------------------------END----------------------------------"
		pass
	def stats(self):
		conn = sql.connect(self.Db_File)
		cur = conn.cursor()
		cur.execute("select * from MLB_V2")
		h_odds_avg = 0.0
		a_odds_avg = 0.0
		h_games_su = 0
		h_games_utd = 0
		a_games_su = 0
		a_games_utd = 0

		h_ev = 0.0
		a_ev = 0.0
		h_ev_su = 0.0
		h_ev_utd = 0.0
		a_ev_su = 0.0
		a_ev_utd = 0.0

		h_ev_interval = []
		a_ev_interval = []

		#insert_game = [season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_half,score_a_half,score_ou,score_ou_half,odds_h,odds_a,odds_h_half,odds_a_half,odds_o,odds_u,odds_o_half,odds_u_half]
		#odds_h 14
		#odds_a 15
		#score_h 8
		#score_a 9
		for fetch in cur.fetchall():
			h_odds_avg += fetch[14]
			a_odds_avg += fetch[15]
			if fetch[14] < fetch[15]:
				h_games_su += 1
				if fetch[8] > fetch[9]:
					h_ev += fetch[14]-1.0
					h_ev_su += fetch[14]-1.0
					a_ev_utd -= 1.0
					a_ev -= 1.0

				else:
					h_ev -= 1.0
					h_ev_su -= 1.0
					a_ev_utd += fetch[15]-1.0
					a_ev += fetch[15]-1.0
			else:
				h_games_utd += 1
				if fetch[8] < fetch[9]:
					a_ev += fetch[15]-1.0
					a_ev_su += fetch[15]-1.0
					h_ev_utd -= 1.0
					h_ev -= 1.0
				else:
					a_ev -= 1.0
					a_ev_su -= 1.0
					h_ev_utd += fetch[14]-1.0
					h_ev += fetch[14]-1.0
		h_odds_avg /= h_games_su+h_games_utd
		a_odds_avg /= h_games_su+h_games_utd
		print h_odds_avg,a_odds_avg,h_games_su,h_games_utd,h_ev,h_ev_su,h_ev_utd,a_ev,a_ev_su,a_ev_utd
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
		#insert_game = [season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_half,score_a_half,score_ou,score_ou_half,odds_h,odds_a,odds_h_half,odds_a_half,odds_o,odds_u,odds_o_half,odds_u_half]
		cur.execute("select * from MLB_V2")
		x= []
		y= [[[] for jj in range(0,12)] for kk in range(0,11)]
		ii = 9
		#arg_num starts from 0-10
#		arg_num = 0
		min = 1000
		max = -1000
		avg = [0.0 for ii in range(0,11)]
		std = [0.0 for ii in range(0,11)]
		temp = [0.0 for ii in range(0,11)]
		for fetch in cur.fetchall():
			arg_list = fetch
			score_diff = arg_list[8]+arg_list[9]
			score_half_diff = arg_list[10]+arg_list[11]-arg_list[13]
#			win_h = arg_list[15]/(arg_list[14]+arg_list[15])
			win_h = arg_list[20]/(arg_list[19]+arg_list[20])
			for arg_num in range(0,11):
				temp = (arg_list[48+arg_num]+arg_list[59+arg_num])/2
				bucket=-1
				if win_h < 0.05:
					bucket=0
				elif win_h < 0.05:
					bucket=1
				elif win_h < 0.5:
					bucket=2
				elif win_h < 0.95:
					bucket=3
				elif win_h < 0.65:
					bucket=4
				else:
					bucket=5
				if score_half_diff<0:
					bucket+=6
					y[arg_num][bucket].append(temp)
				elif score_half_diff>0:
					y[arg_num][bucket].append(temp)

			if temp < min:
				min = temp
			if max < temp:
				max = temp
		np.set_printoptions(precision=2,suppress=True)
		for ii in range(0,11):
			for jj in range(0,6):
				if jj == 2 or jj ==3:
					#print np.average(np.array(y[ii][jj])),np.std(np.array(y[ii][jj])),len(y[ii][jj])
					print np.average(np.array(y[ii][jj]))-np.average(np.array(y[ii][jj+6])),np.std(np.array(y[ii][jj]))-np.std(np.array(y[ii][jj+6])),len(y[ii][jj])
				#print np.average(np.array(y[ii][jj])),np.std(np.array(y[ii][jj])),len(y[ii][jj])
				#print "Avg",np.average(np.array(y[ii][jj])),"Std",np.std(np.array(y[ii][jj])),"Games",len(y[ii][jj])
			#print "-------------------------------------"
		"""
		bins = np.linspace(min-1.0,max+1.0,50)
		plt.hist(y[0],bins,alpha=0.5,label="win<35%")
		plt.hist(y[1],bins,alpha=0.5,label="35%<win<45%",normed=True)
		plt.hist(y[2],bins,alpha=0.5,label="45%<win<50%",normed=True)
		plt.hist(y[3],bins,alpha=0.5,label="50%<win<55%",normed=True)
		plt.hist(y[4],bins,alpha=0.5,label="55%<win<65%",normed=True)
		plt.hist(y[5],bins,alpha=0.5,label="65%<win")
		plt.legend(loc='upper right')
		plt.show()
		"""
np.set_printoptions(precision=2,suppress=True)
myBee = Bee("V2_usa_mlb-2015.db")
#myBee.analysis_run_over()
#myBee.analysis_run_over()
myBee.bet_prob()
myBee = Bee("V2_usa_mlb-2014.db")
myBee.bet_prob()
myBee = Bee("V2_usa_mlb-2013.db")
myBee.bet_prob()
"""
myBee = Bee("V2_usa_mlb-2014.db")
myBee.stats_handi()
myBee = Bee("V2_usa_mlb-2013.db")
myBee.stats_handi()
"""
#myBee.generate_stability([100,3])
#myBee.analysis_votes()
