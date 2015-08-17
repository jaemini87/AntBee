__author__ = 'jaemin'
import sys
import os
import sqlite3 as sql
import numpy
from lxml import html
import requests

#import BeautifulSoup as bs
from bs4 import BeautifulSoup,SoupStrainer
import html2text
import urllib2
class Bank:
	db_file = ""
	def __init__(self,mode):
		finmlb = open("mlb2014.txt",'r')
		fin_line = finmlb.readline()
		str_league,str_year,pagenumber = fin_line.split("|")
		self.db_file = mode+"_"+str_league+str_year+".db"
		pass
#	def get_oddsportal(self):
	def print_db(self):
		db_file = self.db_file
		conn = sql.connect(db_file)
		cur = conn.cursor()
		cur.execute("select * from MLB_SU")
		for pp in cur:
			print pp
	def straight_win(self,nid,team_h,team_a,last_game,home_away):
		"""
		 pass two arguments
		 if home team
		 1: su when home team to every team
		 2: su when home team to every team place match
		 3: su when home team to away team
		 4: su when home team to away team place match
		[8] = su_h
		[9] = su_a
		[10] = run_h
		[11] = run_a
		[12] = ou
		"""
		conn = sql.connect(self.db_file)
		return_list = [0.0 for ii in range(0,8)]
		return_list_nom = [0.0 for ii in range(0,4)]
		return_list_denom = [0.0 for ii in range(0,4)]
		return_itr = [0,0,0,0]
		cur_list = [conn.cursor() for ii in range(0,4)]
		fetch = []
		threshold = 3.1
		max_ratio = [1 for ii in range(0,4)]
		if home_away:
			cur_list[0].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh or team_a=:team_hh)",{"nidd":nid,"team_hh":team_h})
			cur_list[1].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh)",{"nidd":nid,"team_hh":team_h})
			cur_list[2].execute("select * from MLB_SU where nid>:nidd and ((team_h=:team_hh and team_a=:team_aa) or (team_h=:team_aa and team_a=:team_hh))",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
			cur_list[3].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh and team_a=:team_aa)",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
		else:
			cur_list[0].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_aa or team_a=:team_aa)",{"nidd":nid,"team_aa":team_a})
			cur_list[1].execute("select * from MLB_SU where nid>:nidd and (team_a=:team_aa)",{"nidd":nid,"team_aa":team_a})
			cur_list[2].execute("select * from MLB_SU where nid>:nidd and ((team_h=:team_hh and team_a=:team_aa) or (team_h=:team_aa and team_a=:team_hh))",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
			cur_list[3].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh and team_a=:team_aa)",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
		fetch.append(cur_list[0].fetchone())
		fetch.append(cur_list[1].fetchone())
		fetch.append(cur_list[2].fetchone())
		fetch.append(cur_list[3].fetchone())

		while sum(max_ratio) > 0:
			for ii in range(0,4):
				if not fetch[ii]:
					max_ratio[ii] = 0
					pass
				elif return_list[ii*2+1] == -1 and fetch[ii][9-home_away] < -0.1:
					max_ratio[ii] = 0
				elif max_ratio[ii] == 1:
					if fetch[ii][9-home_away] > 0:
						return_list[ii*2] += 1.0*fetch[ii][9-home_away]
						return_list_nom[ii] += 1.0
						return_list_denom[ii] += 1.0
						return_itr[ii] += 1
					elif fetch[ii][9-home_away] > -0.1:
						pass
					else:
						return_list[ii*2+1] += 1.0*fetch[ii][9-home_away]
						return_list_denom[ii] += 1.0
						return_itr[ii] += 1
						return_itr[ii] += 1
				if max_ratio[ii] == 0:
					pass
				else:
					fetch[ii] = cur_list[ii].fetchone()

		conn.close()
		return_list_nom = numpy.array(return_list_nom)
		return_list_denom = numpy.array(return_list_denom)
		nonzeroes = numpy.where(return_list_denom>threshold)
		zeroes = numpy.where(return_list_denom<threshold)
		return_list_nom[nonzeroes] = return_list_nom[nonzeroes]/return_list_denom[nonzeroes]
		return_list_nom[zeroes] = 0
		return return_list_nom
		return return_list
	def over_under(self,nid,team_h,team_a,last_game,home_away):
		"""
		 pass two arguments
		 if home team
		 1: su when home team to every team
		 2: su when home team to every team place match
		 3: su when home team to away team
		 4: su when home team to away team place match
		[8] = su_h
		[9] = su_a
		[10] = run_h
		[11] = run_a
		[12] = ou
		"""
		conn = sql.connect(self.db_file)
		return_list = [0.0 for ii in range(0,8)]
		return_list_nom = [0.0 for ii in range(0,4)]
		return_list_denom = [0.0 for ii in range(0,4)]
		return_itr = [0,0,0,0]
		cur_list = [conn.cursor() for ii in range(0,4)]
		threshold = 3.1
		fetch = []
		max_ratio = [1 for ii in range(0,4)]
		if home_away:
			cur_list[0].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh or team_a=:team_hh)",{"nidd":nid,"team_hh":team_h})
			cur_list[1].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh)",{"nidd":nid,"team_hh":team_h})
			cur_list[2].execute("select * from MLB_SU where nid>:nidd and ((team_h=:team_hh and team_a=:team_aa) or (team_h=:team_aa and team_a=:team_hh))",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
			cur_list[3].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh and team_a=:team_aa)",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
		else:
			cur_list[0].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_aa or team_a=:team_aa)",{"nidd":nid,"team_aa":team_a})
			cur_list[1].execute("select * from MLB_SU where nid>:nidd and (team_a=:team_aa)",{"nidd":nid,"team_aa":team_a})
			cur_list[2].execute("select * from MLB_SU where nid>:nidd and ((team_h=:team_hh and team_a=:team_aa) or (team_h=:team_aa and team_a=:team_hh))",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
			cur_list[3].execute("select * from MLB_SU where nid>:nidd and (team_h=:team_hh and team_a=:team_aa)",{"nidd":nid,"team_hh":team_h,"team_aa":team_a})
		fetch.append(cur_list[0].fetchone())
		fetch.append(cur_list[1].fetchone())
		fetch.append(cur_list[2].fetchone())
		fetch.append(cur_list[3].fetchone())
		while sum(max_ratio) > 0:
			for ii in range(0,4):
				if not fetch[ii]:
					max_ratio[ii] = 0
					pass
				elif return_list[ii*2+1] == -1 and fetch[ii][12] < -0.1:
					max_ratio[ii] = 0
				elif max_ratio[ii] == 1:
					if fetch[ii][12] > 0:
						return_list[ii*2] += 1.0*fetch[ii][12]
						return_list_nom[ii] += 1.0
						return_list_denom[ii] += 1.0
						return_itr[ii] += 1
					elif fetch[ii][12] > -0.1:
						pass
					else:
						return_list[ii*2+1] += 1.0*fetch[ii][12]
						return_list_denom[ii] += 1.0
						return_itr[ii] += 1
						return_itr[ii] += 1
				if max_ratio[ii] == 0:
					pass
				else:
					fetch[ii] = cur_list[ii].fetchone()
		conn.close()
		return_list_nom = numpy.array(return_list_nom)
		return_list_denom = numpy.array(return_list_denom)
		nonzeroes = numpy.where(return_list_denom > threshold)
		zeroes = numpy.where(return_list_denom < threshold)
		return_list_nom[nonzeroes] = return_list_nom[nonzeroes]/return_list_denom[nonzeroes]
		return_list_nom[zeroes] = 0
		return return_list_nom
		return return_list

	def predict_day(self,day,month,year,mode):
		db_file = self.db_file
		conn = sql.connect(db_file)
		cur = conn.cursor()
		cur.execute("select * from MLB_SU where day=:dayy and month=:monthh and year=:yearr",{"dayy":day,"monthh":month,"yearr":year})
		yes_ou = 0.0
		no_ou = 0.0
		for fetch in  cur.fetchall():
			predict = []
			max_ratio = [0.0 for ii in range(0,4)]
			min_ratio = [1.0 for ii in range(0,4)]
			# 1 : SU Home
			# 2 : SU Away
			# 3 : OU Home
			# 4 : OU Away
			last_game = 10
			predict.append(self.straight_win(fetch[0],fetch[6],fetch[7],last_game,1))
			predict.append(self.straight_win(fetch[0],fetch[6],fetch[7],last_game,0))
			predict.append(self.over_under(fetch[0],fetch[6],fetch[7],last_game,1))
			predict.append(self.over_under(fetch[0],fetch[6],fetch[7],last_game,0))
			for ii in range(0,4):
				max_ratio[ii] = max(predict[ii][0],predict[ii][1],predict[ii][2],predict[ii][3])
				min_ratio[ii] = min(predict[ii][0],predict[ii][1],predict[ii][2],predict[ii][3])
#			print predict,fetch
			"""
			last_game = 10
			predict.append(self.straight_win(fetch[0],fetch[6],fetch[7],last_game,1))
			predict.append(self.straight_win(fetch[0],fetch[6],fetch[7],last_game,0))
			predict.append(self.over_under(fetch[0],fetch[6],fetch[7],last_game,1))
			predict.append(self.over_under(fetch[0],fetch[6],fetch[7],last_game,0))
			for ii in range(0,4):
				max_ratio[ii] = max(max_ratio[ii],predict[ii][0],predict[ii][1],predict[ii][2],predict[ii][3])
				min_ratio[ii] = min(max_ratio[ii],predict[ii][0],predict[ii][1],predict[ii][2],predict[ii][3])
			"""
			if max_ratio[2] > 0.7 and max_ratio[3] > 0.7:
				if fetch[12] == 1:
					yes_ou += 1
				elif fetch[12] == -1:
					no_ou += 1
			"""
			elif min_ratio[2] < 0.39 and min_ratio[3] < 0.39:
				if fetch[12] == -1:
					yes_ou += 1
				elif fetch[12] == 1:
					no_ou += 1
			"""
#			print yes_ou,no_ou,numpy.array(max_ratio),fetch
		conn.close()
		return [yes_ou,no_ou]
		pass
	def create_database(self,mode):
		finmlb = open("mlb2014.txt",'r')
		while 1:
			fin_line = finmlb.readline()
			if not fin_line:
				break
			str_league,str_year,pagenumber = fin_line.split("|")
			pagenumber = int(pagenumber)
			command = "mkdir "+ str_league+str_year
			os.system(command)
			start = 2
#			for ii in range(start,pagenumber+1):
			db_file = self.db_file
			for ii in range(start,pagenumber+1):
				outputtxt = "./"+str_league+str_year+"/"+str(ii)+"final.txt"
				"""
				outputpdf = "./"+league+year+"/"+str(ii)+".pdf"
				cacheoption = "--cache-dir ./cache_"+league
				inputurl = "http://www.oddsportal.com/baseball/"+league_url+"/results/#/page/"+str(ii)
				command = "wkhtmltopdf "+cacheoption+" "+inputurl+" "+outputpdf
				os.system(command)
				print command
				command = "pdftotext -raw "+outputpdf+" "+outputtxt
				os.system(command)
				print command
				"""
				fin = open(outputtxt, 'r')
				fin_end = 0
				fin_start = 0
				day = 0
				year = 0
				month = ""
				while 1:
					fin_line = fin.readline()
					if not fin_line: break
					if fin_line.find("1 2 B") != -1:
						fin_start = 1
						if fin_line.find("Play")!= -1 or fin_line.find("Wild") != -1:
							season = "play-off"
						elif fin_line.find("Pre")!= -1:
							season = "pre-season"
						else:
							season = "season"
						day = int(fin_line[0:2])
						if fin_line[2] == " ":
							month = fin_line[3:6]
							year = int(fin_line[7:11])
						else:
							month = fin_line[2:5]
							year = int(fin_line[6:10])

					elif fin_line.find("|") == 0 or fin_line.find("|") == 1 or fin_line.find("Manage")== 0:
						fin_end = 1
						break
					elif fin_line.find("Baseball") == 0:
						fin_en = 1
					elif fin_start == 1 and fin_end == 0:
						conn = sql.connect(db_file)
						cur = conn.cursor()
						score_odds = self.get_game_info_from_str(fin_line)
						endname = max(fin_line.rfind("s"), fin_line.rfind("x"), fin_line.rfind("p"))
						dash = fin_line.find("-")
						team_h  = fin_line[6:dash-1]
						team_a = fin_line[dash+2:endname+1]
						time,score_h,score_a,odds_h,odds_a,score_ou,odds_o,odds_u,score_h_full,score_a_full = score_odds
						hhome = 4
						aaway = 5
						score_h_f = 0
						score_a_f = 0
						score_h_l = 0
						score_a_l = 0
						team_h_shark = self.get_str_team_mlb(self.get_int_team_mlb(team_h))
						team_a_shark = self.get_str_team_mlb(self.get_int_team_mlb(team_a))
						month_shark = self.get_str_month_mlb(month)
						stats_list_28 = []
						su_h  = 1 if (odds_h<odds_a and score_h>score_a) else (-1 if(odds_h<odds_a and score_h<score_a) else 0)
						su_a  = 1 if (odds_a<odds_h and score_a>score_h) else (-1 if(odds_a<odds_h and score_a<score_h) else 0)
						run_h = 1 if (odds_h<odds_a and score_h-1>score_a) else (-1 if(odds_h<odds_a and score_h-1<score_a) else 0)
						run_a = 1 if (odds_a<odds_h and score_a-1>score_h) else (-1 if(odds_a<odds_h and score_a-1<score_h) else 0)
						ou    = 1 if(score_h+score_a > score_ou) else (0 if (score_h+score_a == score_ou ) else -1)
						for ii in range(0,6):
							stats_list_28.append(0)
						for ff in range(0,22):
							stats_list_28.append(0.0)
						if season =="season":
							#day+=1
							"""
							con_w_a,con_w_h,con_o,con_u,\
							era_h,era_a,start_era_h,start_era_a,\
							h_earn_h,h_earn_a,h_allow_h,h_allow_a,\
							bull_h,bull_a,b_off_h,b_off_a,b_def_h,b_def_a = self.get_oddsshark_lxml(team_a_shark,team_h_shark,month_shark,day,year)
							"""
							stats_list_28 = self.get_oddsshark_lxml(team_a_shark,team_h_shark,month_shark,day,year)
#							con_w_a,con_w_h,con_o,con_u = self.get_oddsshark(team_a_shark,team_h_shark,month_shark,day,year)
						for home_itr in score_h_full:
							if hhome > 0:
								score_h_f += home_itr
							else :
								score_h_l += home_itr
							hhome -= 1
						for away_itr in score_a_full:
							if aaway > 0:
								score_a_f += away_itr
							else :
								score_a_l += away_itr
							aaway -= 1
						if mode == "score":
							insert_game = ((season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_f,score_a_f,score_h_l,score_a_l,score_ou,odds_h,odds_a,odds_o,odds_u))
						elif mode =="su":
							insert_game = (season,day,month,year,time,team_h,team_a,su_h,su_a,run_h,run_a,ou,odds_h,odds_a,odds_o,odds_u)
						elif mode =="all":
							insert_game = [season,day,month,year,time,team_h,team_a,\
											su_h,su_a,run_h,run_a,ou,\
											odds_h,odds_a,odds_o,odds_u
											]
							for stat in stats_list_28:
								insert_game.append(stat)
						print insert_game
						#cur.execute("""CREATE TABLE IF NOT EXISTS MLB(nid INTEGER primary key AUTOINCREMENT,day INT,month TEXT,year INT,\
						with conn:
							if mode == "score":
								cur.execute("""CREATE TABLE IF NOT EXISTS MLB(nid INTEGER primary key AUTOINCREMENT,season TEXT,day INT,month TEXT,\
										year INTEGER,time INTEGER, team_h TEXT, team_a TEXT, score_h INTEGER, score_a INTEGER,\
										score_h_f INTEGER,score_a_f INTEGER,score_h_l INTEGER,score_a_l INTEGER,\
										score_ou REAL, odds_h REAL,odds_a REAL,odds_o REAL,odds_u REAL)""")
								cur.executemany("""INSERT INTO MLB(season,day,month,year,time,team_h,team_a,score_h,score_a,score_h_f,score_a_f,score_h_l,score_a_l,score_ou,odds_h,odds_a,odds_o,odds_u)\
											VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(insert_game,))
							elif mode =="su":
								cur.execute("""CREATE TABLE IF NOT EXISTS MLB_SU(nid INTEGER primary key AUTOINCREMENT,season TEXT,day INT,month TEXT,\
										year INTEGER,time INTEGER, team_h TEXT, team_a TEXT, su_h INTEGER, su_a INTEGER, run_h INTEGER, run_a INTEGER, \
										ou INTEGER, odds_h REAL, odds_a REAL, odds_o REAL, odds_u REAL,con_w_h INTEGER,con_w_a INTEGER,con_o INTEGER, con_u INTEGER)""")
								cur.executemany("""INSERT INTO MLB_SU(season,day,month,year,time,team_h,team_a,su_h,su_a,run_h,run_a,ou,odds_h,odds_a,odds_o,odds_u,con_w_h,con_w_a,con_o,con_u)\
											VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,? ,?,?,?,?,?)""",(insert_game,))
							elif mode =="all":
								cur.execute("""CREATE TABLE IF NOT EXISTS MLB_SU(nid INTEGER primary key AUTOINCREMENT,season TEXT,day INT,month TEXT,\
										year INTEGER,time INTEGER, team_h TEXT, team_a TEXT, su_h INTEGER, su_a INTEGER, run_h INTEGER, run_a INTEGER,\
										ou INTEGER, odds_h REAL, odds_a REAL, odds_o REAL, odds_u REAL, P0 INTEGER, P1 INTEGER, C0 INTEGER, C1 INTEGER,\
										C2 INTEGER ,C3 INTEGER, S0 REAL, S1 REAL, S2 REAL, S3 REAL, S4 REAL, S5 REAL, S6 REAL, S7 REAL, S8 REAL, S9 REAL,\
										S10 REAL, S11 REAL, S12 REAL, S13 REAL, S14 REAL, S15 REAL, S16 REAL ,S17 REAL, S18 REAL,S19 REAL, S20 REAL, S21 REAL)""")
								cur.executemany("""INSERT INTO MLB_SU(season,day,month,year,time,team_h,team_a,su_h,su_a,run_h,run_a,ou,odds_h,odds_a,odds_o,odds_u,\
												P0,P1,C0,C1,C2,C3,S0,S1,S2,S3,S4,S5,S6,S7,S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,S18,S19,S20,S21)\
												VALUES(?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?,? , ?,?,?,?)""",(insert_game,))

						conn.commit()
						conn.close()
					# print(fin_line)
				fin.close()
		"""
		conn = sql.connect(db_file)
		cur = conn.cursor()
		cur.execute("SELECT * FROM MLB")
		rows = cur.fetchall()
		for row in rows:
			print row
		"""
		finmlb.close()
		pass
	def get_game_info_from_str(self,fin_line):
		cur_time = int(fin_line[0:2])
		parlen_l = fin_line.find("(")
		endcolon = fin_line[:parlen_l].rfind(":")
		score_h = fin_line[endcolon - 2:endcolon]
		score_a = fin_line[endcolon + 1:endcolon + 3]
		sharp = fin_line.find("#")
		enddot = fin_line[0:sharp].rfind(".")
		endplus = fin_line.rfind("+")
		endminus = fin_line.rfind("-")
		endslash = fin_line.rfind("/")
		slash = fin_line.find("/")
		endpl = max(endplus, endminus)
		odds_h = 0.0
		odds_a = 0.0
		over_under = map(float,fin_line[sharp+1:parlen_l].split())
		score_ou,odds_o,odds_u = over_under
		score_h_full = []
		score_a_full = []
		innings = fin_line.count(":")-2
		inning_s = parlen_l
		for inning_i in range(0,innings):
			comma = fin_line[inning_s:].find(",")
			dott = fin_line[inning_s:].find(":")
			dott += inning_s
			score_h_2 = fin_line[dott-2:dott]
			score_h_1 = fin_line[dott-1:dott]
			score_a_2 = fin_line[dott+1:dott+3]
			score_a_1 = fin_line[dott+1:dott+2]
			if score_h_2.isdigit():
				score_h_full.append(int(score_h_2))
			else:
				if score_h_1 == "X":
					score_h_full.append(0)
				else:
					score_h_full.append(int(score_h_1))
			if score_a_2.isdigit():
				score_a_full.append(int(score_a_2))
			else:
				score_a_full.append(int(score_a_1))
			inning_s += comma+1
		if fin_line.count(".") > 4 and sharp != -1 or (fin_line.count(".") > 1 and sharp == -1):
			odds_h = float(fin_line[enddot - 7:enddot - 2])
			odds_a = float(fin_line[enddot - 2:enddot + 3])
		elif fin_line.count("+") + fin_line.count("-") > 1:
			if fin_line[endpl - 5] == '+':
				odds_h = 1.0 + int(fin_line[endpl - 4:endpl - 1]) / 100.0
			elif fin_line[endpl - 5] == '-':
				odds_h = 1.0 + 100.0 / int(fin_line[endpl - 4:endpl - 1])
			if fin_line[endpl] == '+':
				odds_a = 1.0 + int(fin_line[endpl + 1:endpl + 4]) / 100.0
			elif fin_line[endpl] == '-':
				odds_a = 1.0 + 100.0 / int(fin_line[endpl + 1:endpl + 4])
		else:
			odds_h_denom = 0
			odds_h_nom = 0
			odds_a_denom = 0
			odds_a_nom = 0
			for ii in range(3):
				odds_h_t = fin_line[slash - 1 - ii:slash]
				odds_h_tt = fin_line[slash + 1:slash + 2 + ii]
				odds_a_t = fin_line[endslash - 1 - ii:endslash]
				odds_a_tt = fin_line[endslash + 1:endslash + 2 + ii]
				if odds_h_t.isdigit() == 1:
					odds_h_denom = odds_h_t
				if odds_h_tt.isdigit() == 1:
					odds_h_nom = odds_h_tt
				if odds_a_t.isdigit() == 1:
					odds_a_denom = odds_a_t
				if odds_a_tt.isdigit() == 1:
					odds_a_nom = odds_a_tt
			odds_h = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
			odds_a = 1.0 + int(odds_a_denom) * 1.0 / int(odds_a_nom)
		return [cur_time,int(score_h),int(score_a),odds_h,odds_a,score_ou,odds_o,odds_u,score_h_full,score_a_full]
		pass
	def get_oddsshark_lxml(self,team_a_shark,team_h_shark,month_shark,day,year):
		#power ranking 2 elements
		#stats 22 elements
		#consensus 4 elements
		return_list =[]
		for ii in range(0,6):
			return_list.append(0)
		for ff in range(0,22):
			return_list.append(0.0)
		if str(team_h_shark) == "-1" or str(team_a_shark) == "-1":
			return return_list
		while 1:
			url = "http://www.oddsshark.com/mlb/"+team_a_shark+"-"+team_h_shark+"-odds-"+month_shark+"-"+str(day)+"-"+str(year)
			print url
			try:
				page = requests.get(url)
			except requests.HTTPError,e:
				print e.code
				page = requests.get(url)

			tree = html.fromstring(page.text)

			percent = tree.xpath('//span[@class="consensus_percent"]/text()')
			power = tree.xpath('//span[@class="score"]/text()')
			home = tree.xpath('//span[@class="home"]/text()')
			away = tree.xpath('//span[@class="away"]/text()')
			home_f = map(float,home)
			away_f = map(float,away)
			ii=0
			for span in power:
				if ii == 2:
					break
				ints = ""
				for char in span:
					if len(ints) > 1:
						break
					if char.isdigit():
						ints += char
				return_list[ii] = int(ints)
				ii+=1
			ii=2
			for span in percent:
				ints = ""
				for char in span:
					if len(ints) > 1:
						break
					if char.isdigit():
						ints += char
				return_list[ii] = int(ints)
				ii+=1
			return_list[6:17] = home_f[0:11]
			return_list[17:28] = away_f[0:11]
			print return_list
			if len(return_list) != 28:
				if day == 1:
					return_list =[]
					for ii in range(0,6):
						return_list.append(0)
					for ff in range(0,22):
						return_list.append(0.0)
					return return_list
				else:
					day -= 1
			else:
				return return_list

	def get_oddsshark(self,team_a_shark,team_h_shark,month_shark,day,year):
		if str(team_h_shark) == "-1" or str(team_a_shark) == "-1":
			return [50,50,50,50]
		url = "http://www.oddsshark.com/mlb/"+team_a_shark+"-"+team_h_shark+"-odds-"+month_shark+"-"+str(day)+"-"+str(year)
		print url
#		page = requests.get(url)
		try:
			rr = urllib2.urlopen(url)
			print"urllib2.open"
		except urllib2.HTTPError,e:
			print e.code
			if day == 1:
				url = "http://www.oddsshark.com/mlb/"+team_a_shark+"-"+team_h_shark+"-odds-"+month_shark+"-"+str(31)+"-"+str(year)
				try:
					rr = urllib2.urlopen(url)
				except urllib2.HTTPError,e:
					print e.code
					url = "http://www.oddsshark.com/mlb/"+team_a_shark+"-"+team_h_shark+"-odds-"+month_shark+"-"+str(30)+"-"+str(year)
					try:
						rr = urllib2.urlopen(url)
					except urllib2.HTTPError,e:
						return [50,50,50,50]
			else:
				url = "http://www.oddsshark.com/mlb/"+team_a_shark+"-"+team_h_shark+"-odds-"+month_shark+"-"+str(day-1)+"-"+str(year)
				try:
					rr = urllib2.urlopen(url)
				except urllib2.HTTPError,e:
					return [50,50,50,50]
		links=SoupStrainer("span")
		print "SoupStrainer"
		soup = BeautifulSoup(rr.read(),"lxml",parse_only=links)
		print "BS"
		spann = soup.find_all('span',{'class':'consensus_percent'})
		print "Findall"
		return_list = []
		for span in spann:
			ints = ""
			for char in span.get_text():
				if len(ints) > 1:
					break
				if char.isdigit():
					ints += char
			return_list.append(int(ints))
		print"FOR"
		return return_list
		pass
	def convert_portal_shark(self,date,games,league):
		pass
	def get_int_team_mlb(self,name):
		if name == "Baltimore Orioles":
			return 0
		elif name == "Boston Red Sox":
			return 1
		elif name == "Chicago White Sox":
			return 2
		elif name == "Cleveland Indians":
			return 3
		elif name == 	"Detroit Tigers":
			return 4
		elif name == "Houston Astros":
			return 5
		elif name == "Kansas City Royals":
			return 6
		elif name == "Los Angeles Angels":
			return 7
		elif name == "Minnesota Twins":
			return 8
		elif name == "New York Yankees":
			return 9
		elif name == "Oakland Athletics":
			return 10
		elif name == "Seattle Mariners":
			return 11
		elif name == "Tampa Bay Rays":
			return 12
		elif name == "Texas Rangers":
			return 13
		elif name == "Toronto Blue Jays":
			return 14
		elif name == "Arizona Diamondbacks":
			return 15
		elif name == "Atlanta Braves":
			return 16
		elif name == "Chicago Cubs":
			return 17
		elif name == "Cincinnati Reds":
			return 18
		elif name == "Colorado Rockies":
			return 19
		elif name == "Los Angeles Dodgers":
			return 20
		elif name == "Miami Marlins":
			return 21
		elif name == "Milwaukee Brewers":
			return 22
		elif name == "New York Mets":
			return 23
		elif name == "Philadelphia Phillies":
			return 24
		elif name == "Pittsburgh Pirates":
			return 25
		elif name == "San Diego Padres":
			return 26
		elif name == "San Francisco Giants":
			return 27
		elif name == "St.Louis Cardinals":
			return 28
		elif name == "Washington Nationals":
			return 29
		else:
			return -1
			pass
	def get_str_team_mlb(self,name):
		if name == 0:
			return "baltimore"
		elif name == 1:
			return "boston"
		elif name == 2:
			return "chicago"
		elif name == 3:
			return "cleveland"
		elif name == 4:
			return "detroit"
		elif name == 5:
			return "houston"
		elif name == 6:
			return "kansas-city"
		elif name == 7:
			return "los-angeles"
		elif name == 8:
			return "minnesota"
		elif name == 9:
			return "new-york"
		elif name == 10:
			return "oakland"
		elif name == 11:
			return "seattle"
		elif name == 12:
			return "tampa-bay"
		elif name == 13:
			return "texas"
		elif name == 14:
			return "toronto"
		elif name == 15:
			return "arizona"
		elif name == 16:
			return "atlanta"
		elif name == 17:
			return "chicago"
		elif name == 18:
			return "cincinnati"
		elif name == 19:
			return "colorado"
		elif name == 20:
			return "los-angeles"
		elif name == 21:
			return "miami"
		elif name == 22:
			return "milwaukee"
		elif name == 23:
			return "new-york"
		elif name == 24:
			return "philadelphia"
		elif name == 25:
			return "pittsburgh"
		elif name == 26:
			return "san-diego"
		elif name == 27:
			return "san-francisco"
		elif name == 28:
			return "st-louis"
		elif name == 29:
			return "washington"
		else:
			return -1
			pass
	def get_str_month_mlb(self,month):
		if month == "Jan":
			return "january"
		elif month =="Feb":
			return "february"
		elif month =="Mar":
			return "march"
		elif month =="Apr":
			return "april"
		elif month =="May":
			return "may"
		elif month =="Jun":
			return "june"
		elif month =="Jul":
			return "july"
		elif month =="Aug":
			return "august"
		elif month =="Sep":
			return "september"
		elif month =="Oct":
			return "october"
		elif month =="Nov":
			return "november"
		elif month =="Dec":
			return "december"
		else:
			return "?"
		pass
	def get_int_games(self,games,league):
		for game in games:
			if league=="mlb":
				pass
		pass
	def get_str_games(self,games,league):
		pass
numpy.set_printoptions(precision=2,suppress=True)

myBank = Bank("all")
#myBank.create_database("all")
yes_total = 0.0
no_total = 0.0
#myBank.print_db()
#11 worst
#"""
for ii in range(1,30):
	yes,no = myBank.predict_day(ii,"May",2014,"su")
	yes_total += yes
	no_total += no
	print yes,no
print yes_total,no_total,yes_total/(yes_total+no_total)
#"""
