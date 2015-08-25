___author__ = 'JAEMIN'
"""Genetic Algorithmn Implementation
"""
#!/usr/bin/python
from multiprocessing import Process,Value,Array,Lock,Queue,sharedctypes
import sqlite3 as sql
import random
import numpy as np
import datetime
from Bank import Bank
class Pick:
	def __init__(self):
		self.today = int(datetime.date.today().strftime("%d"))+1
		mode = "all"
		input_file = "MLB_PICK.txt"
		fin = open(input_file,'w')
		fin.write("usa|mlb-2015|1")
		fin.close()
		finmlb = open(input_file,'r')
		fin_line = finmlb.readline()
		str_league,str_year,pagenumber = fin_line.split("|")
		self.db_file = mode+"_"+str_league+str_year+".db"
		myBank = Bank(mode,input_file)
		myBank.create_database(mode)
		pass
	def Training(self):
		conn = sql.connect(self.db_file)
		fit_list = []
		cur = conn.cursor()
		cur.execute("select * from MLB_PICK where day=:dayy ORDER BY nid DESC ",{"dayy":self.today})
		counter = 0
		for fin_line in cur:
			if not fin_line:
				break
			counter+=1
			game_stats = fin_line[6:17]
			home_stats = []
			away_stats = []
			for ii in range(0,6):
				if ii % 2 == 0:
					home_stats.append(fin_line[ii+17])
				else:
					away_stats.append(fin_line[ii+17])
			for ii in range(0,22):
				if ii < 11:
					home_stats.append(fin_line[ii+23])
				else:
					away_stats.append(fin_line[ii+23])
			summ,home_away = self.greedy_game(game_stats,home_stats,away_stats)
			fit_list.append([summ,home_away,game_stats])
			fit_sorted = iter(reversed(sorted(fit_list)))
		for ii in range(0,counter):
			print next(fit_sorted)
		print"--------------------"
		pass
	def result_game_solo(self,fit_sorted1,mode):
		summ1,home_away1,game_stats1 = fit_sorted1
		if abs(home_away1)>1:
			mode1 = "ou"
		else:
			mode1 = "money"
		result1 = self.result_game(game_stats1,mode1,home_away1)
		odds1 = self.odds_game(game_stats1,mode1,home_away1)
		if mode == "money":
			if result1 ==  1:
				return [30.0,30.0*odds1]
			else:
				if odds1 == 0.0 :
					return [0.0,0.0]
				else:
					#					return [30.0/(odds1),0.0]
					return [30.0,0.0]

	def result_game_multi(self,fit_sorted1,fit_sorted2,mode):
		summ1,home_away1,game_stats1 = fit_sorted1
		summ2,home_away2,game_stats2 = fit_sorted2
		if abs(home_away1)>1:
			mode1 = "ou"
		else:
			mode1 = "money"
		if abs(home_away2)>1:
			mode2 = "ou"
		else:
			mode2 = "money"
		result1 = self.result_game(game_stats1,mode1,home_away1)
		result2 = self.result_game(game_stats2,mode2,home_away2)
		odds1 = self.odds_game(game_stats1,mode1,home_away1)
		odds2 = self.odds_game(game_stats2,mode2,home_away2)
		if mode == "money":
			if result1 == result2 == 1:
				return [30.0/(odds1*odds2),30.0]
			else:
				if odds1 == 0.0 or odds2 == 0.0:
					return [0.0,0.0]
				else:
					return [30.0/(odds1*odds2),0.0]
		elif mode == "run":
			if result1 == result2 == 1:
				return [30.0/(odds1*odds2),30.0]
			else:
				if odds1 == 0.0 or odds2 == 0.0:
					return [0.0,0.0]
				else:
					return [30.0/(odds1*odds2),0.0]

	def result_game(self,game_stats,mode,home_away):
		if mode == "money":
			if home_away == 1 :
				if (game_stats[2] == 1 or game_stats[3] == -1):
					return 1
				else:
					return -1
			elif home_away == -1:
				if (game_stats[3] == 1 or game_stats[2] == -1):
					return 1
				else:
					return -1
			else :
				return 0
		elif mode == "run":
			if home_away == 1 and game_stats[4] == 1:
				return 1
			elif home_away == -1 and game_stats[5] == 1:
				return 1
			else :
				return -1
		elif mode == "ou":
			if home_away == 2 and game_stats[6] == 1:
				return 1
			elif home_away == -2 and game_stats[6] == -1:
				return 1
			else :
				return -1
		else:
			return 0
		pass
	def odds_game(self,game_stats,mode,home_away):
		if mode == "money":
			if home_away == 1:
				return game_stats[7]
			elif home_away == -1 :
				return game_stats[8]
			else :
				return 0.0
		elif mode == "run":
			if home_away == 1:
				return game_stats[7]*1.4
			elif home_away == -1 :
				return game_stats[8]*1.4
			else :
				return 0.0
		elif mode == "ou":
			if home_away == 2 :
				return game_stats[9]
			elif home_away == -2 :
				return game_stats[10]
			else :
				return 0.0
		else:
			return 0.0
		pass
	def greedy_game(self,game_stats,home_stats,away_stats):
		home_adv = 0.0
		away_adv = 0.0
		su = home_stats[1]-away_stats[1]
		ou = home_stats[2]-away_stats[2]
		if abs(su)<abs(ou):
			if su > 0 and game_stats[7] < game_stats[8]:
				return [abs(su),1]
			elif su < 0  and game_stats[7] > game_stats[8]:
				return [abs(su),-1]
		else:
			if ou > 0 and game_stats[9] < game_stats[10]:
				return [abs(ou),2]
			elif ou < 0 and game_stats[9] > game_stats[10]:
				return [abs(ou),-2]
			#return [0.0,0.0]
		for ii in range(0,2):
			if ii == 0:
				if home_stats[ii] > away_stats[ii]:
					away_adv += 1.0
				else:
					home_adv += 1.0
			else:
				if home_stats[ii] > away_stats[ii]:
					home_adv += 1.0
				else:
					away_adv += 1.0

		for ii in range(3,len(home_stats)):
			if ii%3 == 0:
				if home_stats[ii] > away_stats[ii]:
					home_adv += 1.0
				else:
					away_adv += 1.0
			else:
				if ii == 8:
					if home_stats[ii] > away_stats[ii]:
						away_adv += 2.0
					else:
						home_adv += 2.0
				else:
					if home_stats[ii] > away_stats[ii]:
						away_adv += 1.0
					else:
						home_adv += 1.0
		"""
		print "---------HOME---------"
		print game_stats
		print home_stats
		print away_stats
		"""
		if abs(home_adv-away_adv) < abs(game_stats[7]-game_stats[8])*10.0:
			if home_adv > away_adv and game_stats[7] < game_stats[8]:
				if game_stats[2] == 1:
					#					print ["HOME SU",home_adv,away_adv,game_stats[7],home_stats[0:3]]
					pass
				else:
					#					print ["HOME SU WRONG",home_adv,away_adv,game_stats[7],home_stats[0:3]]
					pass
				return [1/abs(home_adv-away_adv),1]
			elif home_adv < away_adv and game_stats[7] > game_stats[8]:
				if game_stats[3] == 1:
					#					print ["AWAY SU ",home_adv,away_adv,game_stats[8],away_stats[0:3]]
					pass
				else:
					#					print ["AWAY SU WRONG",home_adv,away_adv,game_stats[8],away_stats[0:3]]
					pass
				return [1/abs(home_adv-away_adv),-1]
			else:
				return [0,0]
		else:
			if home_adv < away_adv and game_stats[7] < game_stats[8]:
				if game_stats[2] == -1:
					#					print ["AWAY UP ",home_adv,away_adv,game_stats[8],away_stats[0:3]]
					pass
				else:
					#					print ["AWAY UP WRONG",home_adv,away_adv,game_stats[8],away_stats[0:3]]
					pass
				return [1/abs(home_adv-away_adv),-1]
			elif home_adv > away_adv and game_stats[7] > game_stats[8]:
				if game_stats[3] == -1:
					#					print ["HOME UP ",home_adv,away_adv,game_stats[7],home_stats[0:3]]
					pass
				else:
					#					print ["HOME UP WRONG",home_adv,away_adv,game_stats[7],home_stats[0:3]]
					pass
				return [1/abs(home_adv-away_adv),1]
			else:
				return [0,0]
		pass
	def predict_game(self,home_chr_stats,away_chr_stats,predict_mode):
		if predict_mode == "add":
			home = sum(home_chr_stats)
			away = sum(away_chr_stats)
			if home > away:
				return [abs(home-away),1]
			else:
				return [abs(home-away),-1]
		elif predict_mode == "consensus":
			if home_chr_stats[1] > away_chr_stats[1]:
				return [home_chr_stats[1],1]
			else:
				return [away_chr_stats[1],-1]
		pass
myPick = Pick()
myPick.Training()
