__author__ = 'jaemin'
import os
import PyPDF2
import sys
import time
from datetime import date
def parser_today_games():
	str_league = "usa"
	str_year = "mlb-2016"
	pagenumber = 1
	command = "mkdir "+ str_league+str_year
	os.system(command)
	print(command)
	ii = date.today()
	outputpdf = "./"+str_league+str_year+"/"+str(ii)+".pdf"
	cacheoption = "--cache-dir ./cache_"+str_league
	inputurl = "http://www.oddsportal.com/baseball/usa/mlb"
	#inputurl = "http://www.oddsportal.com/baseball/usa/mlb"+str(str_year)+"/results/#/page/"+str(ii)
	command = "wkhtmltopdf "+cacheoption+" "+inputurl+" "+outputpdf
	os.system(command)
	print command
	f = open(outputpdf, 'rb')
	pdf = PyPDF2.PdfFileReader(f)
	pgs = pdf.getNumPages()
	key = '/Annots'
	uri = '/URI'
	ank = '/A'
	game_urls = []
	game_over_under = []
	for pg in range(pgs):
		p = pdf.getPage(pg)
		o = p.getObject()
		if o.has_key(key):
			ann = o[key]
			for a in ann:
				u = a.getObject()
				if u.has_key(ank):
					if u[ank].has_key(uri):
						myStr = u[ank][uri]
						if myStr.count("-") > 2 and myStr.find("play-odds") == -1:
							if not game_urls.__contains__("http://www.oddsportal.com" + myStr + "#over-under;1/"):
								#game_urls.append("http://www.oddsportal.com" + myStr + "#over-under;1/")
								game_urls.append(myStr + "#over-under;1/")
	outputtxt = "./"+str_league+str_year+"/"+str(ii)+".txt"
	outputtxt_final = "./"+str_league+str_year+"/final"+str(ii)+".txt"
	for game_url in game_urls:
		fout = open(outputtxt, 'a')
		command = "wkhtmltopdf --cache-dir ./cache " + game_url + " temp.pdf"
		os.system(command)
		command = "pdftotext -raw temp.pdf temp.txt"
		os.system(command)
		team = ""
		score_h = -1
		score_a = -1
		ou = 0.0
		over = 5.0
		under = 0.0

		fin = open("temp.txt", 'r')
		while 1:
			fin_line = fin.readline()
			if not fin_line:
				break
			if fin_line.find("Compare odds") != -1:
				fin_line = fin.readline()
				dot = fin_line.find(".")
				odds_h = 0.0
				odds_a = 0.0
				if fin_line.count(".") > 1:
					ou_t = float(fin_line[dot - 1:dot + 2])
					fin_line = fin.readline()
					if fin_line.find(".")!= -1:
						over_t = float(fin_line)
						fin_line = fin.readline()
						under_t = float(fin_line)
					elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
						if fin_line.find("+") != -1:
							odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
						elif fin_line.find("-") != -1:
							odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
						fin_line = fin.readline()
						if fin_line.find("+") != -1:
							odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
						elif fin_line.find("-") != -1:
							odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
						over_t = odds_h
						under_t = odds_a
					elif fin_line.find("/") != -1:
						odds_h_denom = 0
						odds_h_nom = 0
						slash = fin_line.find("/")
						odds_h_denom = fin_line[0:slash]
						odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
						over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

						fin_line = fin.readline()
						slash = fin_line.find("/")
						odds_h_denom = fin_line[0:slash]
						odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
						under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
					over_t = int(over_t*100)*1.0/100.0
					under_t = int(under_t*100)*1.0/100.0
					if abs(over - under) > abs(over_t - under_t):
						#################Over and under are converted!!##############
						over = under_t
						under = over_t
						ou = ou_t
			elif fin_line.find("PRE-MATCH")!= -1:
				fin_line = fin.readline()
				team = fin_line
			elif fin_line.find("Home")!= -1 and fin_line.find("Baseball")!= -1:
				questionmark = fin_line.rfind("\xbb")
				print fin_line
				mod_team = fin_line[questionmark+1:len(fin_line)-1]
				team = ""
				for ii in range(0,len(mod_team)):
					if mod_team[0] == " " and ii == 0:
						pass
					elif mod_team[ii].isupper() and ii > 2 and mod_team[ii-1] != " " and mod_team[ii-1] != ".":
						team += " "
						team += mod_team[ii]
					else:
						team += mod_team[ii]
				print "--------------"
				print mod_team
				print team
				print "--------------"
			elif fin_line.find("9th Inning")!= -1 or fin_line.find("Final result")!= -1:
				colon = fin_line.find(":")
				if colon == -1:
					score_h = 0
					score_a = 0
				if fin_line[colon-2:colon].isdigit():
					score_h = int(fin_line[colon-2:colon])
				elif fin_line[colon-1:colon].isdigit():
					score_h = int(fin_line[colon-1:colon])
				else:
					score_h = 0
				if fin_line[colon+1:colon+3].isdigit():
					score_a = int(fin_line[colon+1:colon+3])
				elif fin_line[colon+1:colon+2].isdigit():
					score_a = int(fin_line[colon+1:colon+2])
				else:
					score_a = 0

		fin.close()
		temp = [team,score_h,score_a,ou,over,under]
		game_over_under.append(temp)
		for kkk in temp:
			fout.write(str(kkk)+"#")
		fout.write("\n")
		fout.close()
		print [team,score_h,score_a,ou,over,under]
	#fout.close()
	##########################################################Game Over Under Parsing###################################
	command = "pdftotext -raw "+outputpdf+" "+outputtxt
	os.system(command)
	print command

	fin = open(outputtxt, 'r')
	fout = open(outputtxt_final, 'w')
	fin_en = 0
	fin_past = ""
	while 1:
		fin_line = fin.readline()
		if not fin_line: break
		if fin_line.find("|") == 0 or fin_line.find("|") == 1:
			fin_en = 0
			break
		if fin_en == 1:
			found  = 0
			game_dup = []
			for kkk in game_over_under:
				team,score_h,score_a,ou,over,under,score_h_full,score_a_full = kkk
				score = str(score_h)+":"+str(score_a)
				dash = str(team).find("-")
				dash2 = fin_line.find("-")
				if len(fin_line) < 12 or fin_line.find("-") == -1:
					continue
				elif (fin_line[6:9] == team[0:3] and fin_line[dash2+2:dash2+5] == team[dash+2:dash+5]):
					if not game_dup:
						fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+"\n")
						found = 1
						game_dup.append(kkk)
						break
					elif not game_dup.__contains__(kkk):
						fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+"\n")
						found = 1
						game_dup.append(kkk)
						break
			if found == 0:
				print "has not found any game"
				fout.write(fin_line[0:len(fin_line)-1]+"#"+str(7.3)+" "+str(1.9)+" "+str(1.9)+"\n")
			#sys.exit(1)
		# print(fin_line)
		if fin_line.find("Baseball") == 0:
			fin_en = 1
		# print(fin_line)
	fin.close()
	fout.close()
	print game_over_under
	return game_over_under
def txt_parser_ah_half(file_name):
	fin_ah = open(file_name, 'r')
	team = ""
	score_h = -1
	score_a = -1
	ou = 0.0
	ou_full = 0.0
	ou_half = 0.0
	over = 5.0
	under = 5.0
	over_full = 5.0
	under_full = 0.0
	over_half = 1.5
	under_half = 0.0
	odds_h_half = 1.9
	odds_a_half = 1.9
	over_t = 1.9
	under_t = 1.9
	parse = 0
	while 1:
		fin_line = fin_ah.readline()
		if not fin_line:
			break
		odds_h = 0.0
		odds_a = 0.0
		if (fin_line.count(".") < 2 and fin_line.find("sian") != -1 and fin_line.find("%") != -1) :
			fin_line = fin_ah.readline()
			if fin_line.find(".")!= -1:
				over_t = float(fin_line)
				fin_line = fin_ah.readline()
				under_t = float(fin_line)
				parse = 1
			elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
				if fin_line.find("+") != -1:
					odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				fin_line = fin_ah.readline()
				if fin_line.find("+") != -1:
					odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				over_t = odds_h
				under_t = odds_a
				parse = 1
			elif fin_line.find("/") != -1:
				odds_h_denom = 0
				odds_h_nom = 0
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

				fin_line = fin_ah.readline()
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
				parse = 1
			over_t = int(over_t*100)*1.0/100.0
			under_t = int(under_t*100)*1.0/100.0
			odds_h_half = under_t
			odds_a_half = over_t
			fin_ah.close()
			break
	if parse == 0:
		fin_ah = open(file_name)
		while 1:
			fin_line = fin_ah.readline()
			if not fin_line:
				break
			odds_h = 0.0
			odds_a = 0.0
			if fin_line[0] =="0":
				dot = fin_line.find(".")
				rdot = fin_line.rfind(".")
				plus = fin_line[1:].find("+")
				rplus = fin_line[1:].find("+")
				minus = fin_line[:-2].find("-")
				rminus = fin_line[:-2].find("-")
				dash = fin_line.find("/")
				rdash = fin_line.find("/")
				if dot != -1:
					over_t = float(fin_line[dot-1:dot+3])
					under_t = float(fin_line[rdot-1:rdot+3])
				elif plus != -1:
					if plus+1 < minus:
						odds_h = 1.0 + int(fin_line[plus+2:plus+5]) / 100.0
						odds_a = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
					elif minus < plus:
						odds_h = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
						odds_a = 1.0 + int(fin_line[plus+2:plus+5]) / 100.0
					over_t = odds_h
					under_t = odds_a
				elif plus == -1 and fin_line.count("-") > 2:
					odds_h = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
					odds_a = 1.0 + 100.0 / int(fin_line[rminus+1:rminus+4])
				elif dash != -1:
					odds_h_denom = 0
					odds_h_nom = 0
					slash = dash
					odds_h_denom = fin_line[slash-2:slash]
					odds_h_nom = fin_line[slash + 1:slash+4]
					over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
					slash = rdash
					odds_h_denom = fin_line[slash-2:slash]
					odds_h_nom = fin_line[slash + 1:slash+4]
					under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
				over_t = int(over_t*100)*1.0/100.0
				under_t = int(under_t*100)*1.0/100.0
				odds_h_half = under_t
				odds_a_half = over_t
				fin_ah.close()
				break
	if parse == 0 and odds_h_half == 1.9 and odds_a_half == 1.9:
		print file_name
	return [odds_h_half,odds_a_half]
	pass
def txt_parser_ou_half(file_name):
	fin = open(file_name,'r')
	team = ""
	score_h = -1
	score_a = -1
	ou = 0.0
	ou_full = 0.0
	ou_half = 0.0
	over = 5.0
	under = 0.0
	over_full = 5.0
	under_full = 0.0
	over_half = 1.5
	under_half = 0.0
	odds_h_half = 1.9
	odds_a_half = 1.9
	while 1:
		fin_line = fin.readline()
		if not fin_line:
			break
		dot = fin_line.find(".")
		plus = fin_line.find("+")
		odds_h = 0.0
		odds_a = 0.0
		#if fin_line.count(".") > 1:
		if fin_line.find("+") != -1 and fin_line.find("%") != -1 and fin_line.find("Over") != -1:
			ou_t = float(fin_line[dot - 1:dot + 2])
			if fin_line.count(".") > 1:
				ou_t = float(fin_line[plus+1:plus+4])
			else:
				ou_t = float(fin_line[plus+1:plus+2])
			fin_line = fin.readline()
			if fin_line.find(".")!= -1:
				over_t = float(fin_line)
				fin_line = fin.readline()
				under_t = float(fin_line)
			elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
				if fin_line.find("+") != -1:
					odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				fin_line = fin.readline()
				if fin_line.find("+") != -1:
					odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				over_t = odds_h
				under_t = odds_a
			elif fin_line.find("/") != -1:
				odds_h_denom = 0
				odds_h_nom = 0
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

				fin_line = fin.readline()
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
			over_t = int(over_t*100)*1.0/100.0
			under_t = int(under_t*100)*1.0/100.0
			if abs(over - under) > abs(over_t - under_t):
				############Conver the value!!#############
				over = under_t
				under = over_t
				ou = ou_t
	fin.close()
	fin = open(file_name,'r')
	if over == 5.0 and under == 0.0:
		print file_name
		over = 1.9
		under = 1.9
		ou = 4.0
		while 1:
			fin_line = fin.readline()
			if not fin_line:
				break
			#if fin_line.count(".") > 1:
			if fin_line.find("Bookmaker") != -1:
				fin_line = fin.readline()
				dot = fin_line.find(".")
				rdot = fin_line.rfind(".")
				plus = fin_line[1:].find("+")
				rplus = fin_line[1:].find("+")
				minus = fin_line[:-2].find("-")
				rminus = fin_line[:-2].find("-")
				dash = fin_line.find("/")
				rdash = fin_line.find("/")
				odds_h = 0.0
				odds_a = 0.0
				if fin_line.find("+") != -1 and fin_line.find("-") != -1:
					if fin_line[2] == ".":
						ou_t = float(fin_line[1:4])
					else:
						ou_t = float(fin_line[1:2])
					if fin_line.count(".") > 2:
						dot2 = fin_line[dot+1:].find(".")
						over_t = float(fin_line[dot+1+dot2:dot+dot2+3])
						under_t = float(fin_line[rdot-1:rdot+3])
					elif fin_line.count(".") == 2:
						over_t = float(fin_line[dot-1:dot+3])
						under_t = float(fin_line[rdot-1:rdot+3])
					elif plus != -1:
						if plus+1 < minus:
							odds_h = 1.0 + int(fin_line[plus+2:plus+5]) / 100.0
							odds_a = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
						elif minus < plus:
							odds_h = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
							odds_a = 1.0 + int(fin_line[plus+2:plus+5]) / 100.0
						over_t = odds_h
						under_t = odds_a
					elif plus == -1 and fin_line.count("-") > 2:
						odds_h = 1.0 + 100.0 / int(fin_line[minus+1:minus+4])
						odds_a = 1.0 + 100.0 / int(fin_line[rminus+1:rminus+4])

					elif dash != -1:
						odds_h_denom = 0
						odds_h_nom = 0
						slash = dash
						odds_h_denom = fin_line[slash-2:slash]
						odds_h_nom = fin_line[slash + 1:slash+4]
						over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
						slash = rdash
						odds_h_denom = fin_line[slash-2:slash]
						odds_h_nom = fin_line[slash + 1:slash+4]
						under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
					over_t = int(over_t*100)*1.0/100.0
					under_t = int(under_t*100)*1.0/100.0
					if abs(over - under) > abs(over_t - under_t):
						############Conver the value!!#############
						over = under_t
						under = over_t
						ou = ou_t
	if over == 5.0 and under == 0.0:
		print file_name
		over = 1.9
		under = 1.9
		ou = 4.0
	fin.close()
	return [ou,over,under]
	pass
def txt_parser_ou_full(file_name):
	team = ""
	score_h = -1
	score_a = -1
	ou = 0.0
	ou_full = 0.0
	ou_half = 0.0
	over = 5.0
	under = 0.0
	over_full = 5.0
	under_full = 0.0
	over_half = 1.5
	under_half = 0.0
	odds_h_half = 1.9
	odds_a_half = 1.9
	score_full = []
	score_h_full = []
	score_a_full = []
	fin = open(file_name,'r')
	while 1:
		fin_line = fin.readline()
		if not fin_line:
			break
		dot = fin_line.find(".")
		plus = fin_line.find("+")
		odds_h = 0.0
		odds_a = 0.0
		#if fin_line.count(".") > 1:
		if fin_line.find("+") != -1 and fin_line.find("%") != -1 and fin_line.find("Over") != -1:
			ou_t = float(fin_line[dot - 1:dot + 2])
			if fin_line.count(".") > 1:
				ou_t = float(fin_line[plus+1:plus+4])
			else:
				ou_t = float(fin_line[plus+1:plus+2])
			fin_line = fin.readline()
			if fin_line.find(".")!= -1:
				over_t = float(fin_line)
				fin_line = fin.readline()
				under_t = float(fin_line)
			elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
				if fin_line.find("+") != -1:
					odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				fin_line = fin.readline()
				if fin_line.find("+") != -1:
					odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
				elif fin_line.find("-") != -1:
					odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
				over_t = odds_h
				under_t = odds_a
			elif fin_line.find("/") != -1:
				odds_h_denom = 0
				odds_h_nom = 0
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

				fin_line = fin.readline()
				slash = fin_line.find("/")
				odds_h_denom = fin_line[0:slash]
				odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
				under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
			over_t = int(over_t*100)*1.0/100.0
			under_t = int(under_t*100)*1.0/100.0
			if abs(over - under) > abs(over_t - under_t):
				############Conver the value!!#############
				over = under_t
				under = over_t
				ou = ou_t

		elif fin_line.find("PRE-MATCH")!= -1:
			fin_line = fin.readline()
			team = fin_line
		elif fin_line.find("Home")!= -1 and fin_line.find("Baseball")!= -1:
			questionmark = fin_line.rfind("\xbb")
			mod_team = fin_line[questionmark+1:len(fin_line)-1]
			team = ""
			for ii in range(0,len(mod_team)):
				if mod_team[0] == " " and ii == 0:
					pass
				elif mod_team[ii].isupper() and ii > 2 and mod_team[ii-1] != " " and mod_team[ii-1] != ".":
					team += " "
					team += mod_team[ii]
				else:
					team += mod_team[ii]
			"""
			print "--------------"
			print mod_team
			print team
			print "--------------"
			"""
		elif fin_line.find("9th Inning")!= -1 or fin_line.find("Final result")!= -1:
			colon = fin_line.find(":")
			parlen_l = fin_line.find("(")
			score_h_full = []
			score_a_full = []
			innings = fin_line.count(":")-1
			inning_s = parlen_l
			score_full = fin_line[inning_s:]
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
					if score_a_1 == "X":
						score_h_full.append(0)
					else:
						score_a_full.append(int(score_a_1))
				inning_s += comma+1
			if colon == -1:
				score_h = 0
				score_a = 0
			if fin_line[colon-2:colon].isdigit():
				score_h = int(fin_line[colon-2:colon])
			elif fin_line[colon-1:colon].isdigit():
				score_h = int(fin_line[colon-1:colon])
			else:
				score_h = 0
			if fin_line[colon+1:colon+3].isdigit():
				score_a = int(fin_line[colon+1:colon+3])
			elif fin_line[colon+1:colon+2].isdigit():
				score_a = int(fin_line[colon+1:colon+2])
			else:
				score_a = 0
#	if score_h != sum(score_h_full) or score_a != sum(score_a_full) and(sum(score_h_full) + sum(score_a_full) != 0):
#		print "ERROR"
	fin.close()
	if over == 5.0 and under == 0.0:
		print file_name
		over = 1.9
		under = 1.9
		ou = 7.3
	return [team,score_h,score_a,ou,over,under,score_full]
	pass
def Parser(itr,db_file_itr):
	"""
	finmlb = open(input_file,'r')
	fin_line = finmlb.readline()
	str_league,str_year,pagenumber = fin_line.split("|")
	pagenumber = int(pagenumber)
	command = "mkdir "+ str_league+str_year
	os.system(command)
	print(command)
	"""
	mode,str_league,str_year,pagenumber = db_file_itr
	ii = itr
	outputpdf = "./"+str_league+str_year+"/"+str(ii)+".pdf"
	if mode == "half":
		outputtxt_final = "./"+str_league+str_year+"/"+str(ii)+str(mode)+"_final.txt"
	elif mode == "v2":
		outputtxt_final = "./"+str_league+str_year+"/final"+str(ii)+str(mode)+".txt"
	else:
		outputtxt_final = "./"+str_league+str_year+"/"+str(ii)+"final.txt"
	try:
		f = open(outputpdf, 'rb')
	except:
		cacheoption = "--cache-dir ./cache_"+str_league
		inputurl = "http://www.oddsportal.com/baseball/usa/"+str(str_year)+"/results/#/page/"+str(ii)
		command = "wkhtmltopdf "+cacheoption+" "+inputurl+" "+outputpdf
		os.system(command)
		print command
		f = open(outputpdf, 'rb')
		pass
	pdf = PyPDF2.PdfFileReader(f)
	pgs = pdf.getNumPages()
	key = '/Annots'
	uri = '/URI'
	ank = '/A'
	game_urls = []
	game_over_under = []
	for pg in range(pgs):
		p = pdf.getPage(pg)
		o = p.getObject()
		if o.has_key(key):
			ann = o[key]
			for a in ann:
				u = a.getObject()
				if u.has_key(ank):
					if u[ank].has_key(uri):
						myStr = u[ank][uri]
						if myStr.count("-") > 2 and myStr.find("play-odds") == -1:
							if not game_urls.__contains__("http://www.oddsportal.com" + myStr):
								#game_urls.append("http://www.oddsportal.com" + myStr + "#over-under;1/")
								if myStr.find("oddsportal") != -1:
									game_urls.append(myStr)
								else:
									game_urls.append("http://www.oddsportal.com" + myStr)

	outputtxt = "./"+str_league+str_year+"/temp"+str(ii)+str(mode)+".txt"
	print game_urls
	for game_url in game_urls:
		fout = open(outputtxt, 'w')
		team = ""
		score_h = -1
		score_a = -1
		ou = 0.0
		ou_full = 0.0
		ou_half = 0.0
		over = 5.0
		under = 5.0
		over_full = 5.0
		under_full = 0.0
		over_half = 1.5
		under_half = 0.0
		odds_h_half = 1.9
		odds_a_half = 1.9
		if mode == "half":
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;3 temp_ou.pdf"
			os.system(command)
			print command
			command = "pdftotext -raw temp_ou_half.pdf temp_ou_half.txt"
			[team,score_h,score_a,ou_full,over_full,under_full,score_full] = txt_parser_ou_half("temp_ou_full.txt")
			os.system(command)
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#ah;3 temp_ah.pdf"
			print command
			os.system(command)
			command = "pdftotext -raw temp_ah_half.pdf temp_ah_half.txt"
			os.system(command)
		elif mode == "v2":
			count = 0
			game_url_mod = ""
			for ii in game_url:
				if ii == "/" and count == 6:
					break
				elif count == 6:
					game_url_mod += ii
				if ii == "/":
					count += 1
			try:
				outputtxt_temp = "./"+str_league+str_year+"/"+str(game_url_mod)+"_ou_full.txt"
				fin = open(outputtxt_temp,'r')
			except:
				command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;1 temp_ou_full.pdf"
				os.system(command)
				command = "pdftotext -raw temp_ou_full.pdf "+outputtxt_temp
				os.system(command)
			[team,score_h,score_a,ou_full,over_full,under_full,score_full] = txt_parser_ou_full(outputtxt_temp)
			try:
				outputtxt_temp = "./"+str_league+str_year+"/"+str(game_url_mod)+"_ou_half.txt"
				fin = open(outputtxt_temp,'r')
			except:
				command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;3 temp_ou_half.pdf"
				os.system(command)
				print command
				command = "pdftotext -raw temp_ou_half.pdf "+outputtxt_temp
				os.system(command)
			[ou_half,over_half,under_half] = txt_parser_ou_half(outputtxt_temp)
			try:
				outputtxt_temp = "./"+str_league+str_year+"/"+str(game_url_mod)+"_ah_half.txt"
				fin = open(outputtxt_temp,'r')
			except:
				command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#ah;3 temp_ah_half.pdf"
				print command
				os.system(command)
				command = "pdftotext -raw temp_ah_half.pdf "+outputtxt_temp
				os.system(command)
			[odds_h_half,odds_a_half] = txt_parser_ah_half(outputtxt_temp)
		else :
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;1 temp_ou.pdf"
			os.system(command)
			command = "pdftotext -raw temp_ou.pdf temp_ou.txt"
			os.system(command)
			[team,score_h,score_a,ou_full,over_full,under_full,score_full] = txt_parser_ou_full("temp_ou.txt")

		if mode == "half":
			temp = [team,score_h,score_a,odds_h_half,odds_a_half,ou,over,under,score_full]
		elif mode == "v2":
			temp = [team,score_h,score_a,odds_h_half,odds_a_half,ou_full,ou_half,over_full,under_full,over_half,under_half,score_full]
		else:
			temp = [team,score_h,score_a,ou,over,under,score_full]
		game_over_under.append(temp)
		"""
		for kkk in temp:
			fout.write(str(kkk)+"#")
		fout.write("\n")
		fout.close()
		print temp
		"""
	#fout.close()
##########################################################Game Over Under Parsing###################################
	command = "pdftotext -raw "+outputpdf+" "+outputtxt
	os.system(command)
	print command

	fin = open(outputtxt, 'r')
	fout = open(outputtxt_final, 'w')
	fin_en = 0
	fin_past = ""
	while 1:
		fin_line = fin.readline()
		#print(fin_line)
		if not fin_line: break
		if fin_line.find("|") == 0 or fin_line.find("|") == 1:
			fin_en = 0
			break
		if fin_en == 1:
			found  = 0
			game_dup = []
			for kkk in game_over_under:
				if mode == "half":
					team,score_h,score_a,score_h_half,score_a_half,ou,over,under,score_full = kkk
				elif mode == "v2":
					team,score_h,score_a,odds_h_half,odds_a_half,ou_full,ou_half,over_full,under_full,over_half,under_half,score_full = kkk
				else:
					team,score_h,score_a,ou,over,under,score_full = kkk
				score = str(score_h)+":"+str(score_a)
				dash = str(team).find("-")
				dash2 = fin_line.find("-")
				if len(fin_line) < 12 or fin_line.find("-") == -1:
					continue
				elif (fin_line[6:9] == team[0:3] and fin_line[dash2+2:dash2+5] == team[dash+2:dash+5])\
					and fin_line.find(score) != -1 and (fin_line.find("canc") == -1 and fin_line.find("post") == -1):
					if not game_dup:
						if mode == "half":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(score_h_half)+" "+str(score_a_half)+" "+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						elif mode =="v2":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(odds_h_half)+" "+str(odds_a_half)+" "+str(ou_full)+" "+str(ou_half)+" " +str(over_full)+" "+str(under_full)+" "+str(over_half)+" "+str(under_half)+" "+str(score_full))
						else:
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						found = 1
						game_dup.append(kkk)
						break
					elif not game_dup.__contains__(kkk):
						if mode == "half":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(score_h_half)+" "+str(score_a_half)+" "+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						elif mode =="v2":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(odds_h_half)+" "+str(odds_a_half)+" "+str(ou_full)+" "+str(ou_half)+" " +str(over_full)+" "+str(under_full)+" "+str(over_half)+" "+str(under_half)+" "+str(score_full))
						else:
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						found = 1
						game_dup.append(kkk)
						break
			if found == 0 and fin_line.find("canc") == -1 and fin_line.find("post") == -1:
			#if found == 0 :
				print "has not found any game"
				if mode == "half":
					fout.write(fin_line[0:len(fin_line)-1]+"#"+str(1.9)+" "+str(1.9)+" "+str(7.3)+" "+str(1.9)+" "+str(1.9)+" (0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0)"+"\n")
				elif mode =="v2":
					fout.write(fin_line[0:len(fin_line)-1]+"# 1.86 1.86 7.3 4.3 1.86 1.86 1.86 1.86 (0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0)"+"\n")
				else:
					fout.write(fin_line[0:len(fin_line)-1]+"#"+str(7.3)+" "+str(1.9)+" "+str(1.9)+" (0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0)"+"\n")
				#sys.exit(1)
		# print(fin_line)
		if fin_line.find("Baseball") == 0:
			fin_en = 1
			# print(fin_line)
	fin.close()
	fout.close()
#Parser("mlb.txt")
#parser_today_games()































	"""
	self.txt_parser(file_name)
	fin = open("temp_ou_full.txt", 'r')
	if mode =="half" or mode =="v2":
		fin_ah = open("temp_ah_half.txt", 'r')
		while 1:
			fin_line = fin_ah.readline()
			if not fin_line:
				break
			if fin_line.find("Compare odds") != -1:
				fin_line = fin_ah.readline()
				odds_h = 0.0
				odds_a = 0.0
				if fin_line.count(".") < 2 and fin_line.find("Asian") != -1:
					fin_line = fin_ah.readline()
					if fin_line.find(".")!= -1:
						over_t = float(fin_line)
						fin_line = fin_ah.readline()
						under_t = float(fin_line)
					elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
						if fin_line.find("+") != -1:
							odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
						elif fin_line.find("-") != -1:
							odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
						fin_line = fin_ah.readline()
						if fin_line.find("+") != -1:
							odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
						elif fin_line.find("-") != -1:
							odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
						over_t = odds_h
						under_t = odds_a
					elif fin_line.find("/") != -1:
						odds_h_denom = 0
						odds_h_nom = 0
						slash = fin_line.find("/")
						odds_h_denom = fin_line[0:slash]
						odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
						over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

						fin_line = fin_ah.readline()
						slash = fin_line.find("/")
						odds_h_denom = fin_line[0:slash]
						odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
						under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
					over_t = int(over_t*100)*1.0/100.0
					under_t = int(under_t*100)*1.0/100.0
					odds_h_half = over_t
					odds_a_half = under_t
					fin_ah.close()
					break

	while 1:
		fin_line = fin.readline()
		if not fin_line:
			break
		if fin_line.find("Compare odds") != -1:
			fin_line = fin.readline()
			dot = fin_line.find(".")
			odds_h = 0.0
			odds_a = 0.0
			if fin_line.count(".") > 1:
				ou_t = float(fin_line[dot - 1:dot + 2])
				fin_line = fin.readline()
				if fin_line.find(".")!= -1:
					over_t = float(fin_line)
					fin_line = fin.readline()
					under_t = float(fin_line)
				elif fin_line.find("+") != -1 or fin_line.find("-") != -1:
					if fin_line.find("+") != -1:
						odds_h = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
					elif fin_line.find("-") != -1:
						odds_h = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
					fin_line = fin.readline()
					if fin_line.find("+") != -1:
						odds_a = 1.0 + int(fin_line[1:len(fin_line)-1]) / 100.0
					elif fin_line.find("-") != -1:
						odds_a = 1.0 + 100.0 / int(fin_line[1:len(fin_line)-1])
					over_t = odds_h
					under_t = odds_a
				elif fin_line.find("/") != -1:
					odds_h_denom = 0
					odds_h_nom = 0
					slash = fin_line.find("/")
					odds_h_denom = fin_line[0:slash]
					odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
					over_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)

					fin_line = fin.readline()
					slash = fin_line.find("/")
					odds_h_denom = fin_line[0:slash]
					odds_h_nom = fin_line[slash + 1:len(fin_line)-1]
					under_t = 1.0 + int(odds_h_denom) * 1.0 / int(odds_h_nom)
				over_t = int(over_t*100)*1.0/100.0
				under_t = int(under_t*100)*1.0/100.0
				if abs(over - under) > abs(over_t - under_t):
					############Conver the value!!#############
					over = under_t
					under = over_t
					ou = ou_t

		elif fin_line.find("PRE-MATCH")!= -1:
			fin_line = fin.readline()
			team = fin_line
		elif fin_line.find("Home")!= -1 and fin_line.find("Baseball")!= -1:
			questionmark = fin_line.rfind("\xbb")
			print fin_line
			mod_team = fin_line[questionmark+1:len(fin_line)-1]
			team = ""
			for ii in range(0,len(mod_team)):
				if mod_team[0] == " " and ii == 0:
					pass
				elif mod_team[ii].isupper() and ii > 2 and mod_team[ii-1] != " " and mod_team[ii-1] != ".":
					team += " "
					team += mod_team[ii]
				else:
					team += mod_team[ii]
			print "--------------"
			print mod_team
			print team
			print "--------------"
		elif fin_line.find("9th Inning")!= -1 or fin_line.find("Final result")!= -1:
			colon = fin_line.find(":")
			parlen_l = fin_line.find("(")
			score_h_full = []
			score_a_full = []
			innings = fin_line.count(":")-2
			inning_s = parlen_l
			score_full = fin_line[inning_s:]
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
			if colon == -1:
				score_h = 0
				score_a = 0
			if fin_line[colon-2:colon].isdigit():
				score_h = int(fin_line[colon-2:colon])
			elif fin_line[colon-1:colon].isdigit():
				score_h = int(fin_line[colon-1:colon])
			else:
				score_h = 0
			if fin_line[colon+1:colon+3].isdigit():
				score_a = int(fin_line[colon+1:colon+3])
			elif fin_line[colon+1:colon+2].isdigit():
				score_a = int(fin_line[colon+1:colon+2])
			else:
				score_a = 0
	fin.close()
	"""
