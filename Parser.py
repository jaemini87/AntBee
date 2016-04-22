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
	outputtxt_final = "./"+str_league+str_year+"/"+str(ii)+"final.txt"
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
	else:
		outputtxt_final = "./"+str_league+str_year+"/"+str(ii)+"final.txt"
	cacheoption = "--cache-dir ./cache_"+str_league
	inputurl = "http://www.oddsportal.com/baseball/usa/"+str(str_year)+"/results/#/page/"+str(ii)
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
							if not game_urls.__contains__("http://www.oddsportal.com" + myStr):
								#game_urls.append("http://www.oddsportal.com" + myStr + "#over-under;1/")
								game_urls.append(myStr)
	outputtxt = "./"+str_league+str_year+"/"+str(ii)+".txt"
	for game_url in game_urls:
		fout = open(outputtxt, 'a')
		if mode != "half":
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;1 temp_ou.pdf"
			os.system(command)
			command = "pdftotext -raw temp_ou.pdf temp_ou.txt"
			os.system(command)
		else:
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#over-under;3 temp_ou.pdf"
			os.system(command)
			print command
			command = "pdftotext -raw temp_ou.pdf temp_ou.txt"
			os.system(command)
			command = "wkhtmltopdf --cache-dir ./cache " + game_url + "#ah;3 temp_ah.pdf"
			print command
			os.system(command)
			command = "pdftotext -raw temp_ah.pdf temp_ah.txt"
			os.system(command)
		team = ""
		score_h = -1
		score_a = -1
		ou = 0.0
		over = 5.0
		under = 0.0
		odds_h_opt = 1.9
		odds_a_opt = 1.9
		fin = open("temp_ou.txt", 'r')
		if mode =="half":
			fin_ah = open("temp_ah.txt", 'r')
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
						odds_h_opt = over_t
						odds_a_opt = under_t
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
		if mode == "half":
			temp = [team,score_h,score_a,odds_h_opt,odds_a_opt,ou,over,under,score_full]
		else:
			temp = [team,score_h,score_a,ou,over,under,score_full]
		game_over_under.append(temp)
		for kkk in temp:
			fout.write(str(kkk)+"#")
		fout.write("\n")
		fout.close()
		print temp
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
		# print(fin_line)
		if not fin_line: break
		if fin_line.find("|") == 0 or fin_line.find("|") == 1:
			fin_en = 0
			break
		if fin_en == 1:
			found  = 0
			game_dup = []
			for kkk in game_over_under:
				if mode == "half":
					team,score_h,score_a,score_h_opt,score_a_opt,ou,over,under,score_full = kkk
				else:
					team,score_h,score_a,ou,over,under,score_full = kkk
				score = str(score_h)+":"+str(score_a)
				dash = str(team).find("-")
				dash2 = fin_line.find("-")
				if len(fin_line) < 12 or fin_line.find("-") == -1:
					continue
				elif (fin_line[6:9] == team[0:3] and fin_line[dash2+2:dash2+5] == team[dash+2:dash+5])\
					and fin_line.find(score) != -1:
					if not game_dup:
						if mode == "half":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(score_h_opt)+" "+str(score_a_opt)+" "+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						else:
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						found = 1
						game_dup.append(kkk)
						break
					elif not game_dup.__contains__(kkk):
						if mode == "half":
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(score_h_opt)+" "+str(score_a_opt)+" "+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						else:
							fout.write(fin_line[0:len(fin_line)-1]+"#"+str(ou)+" "+str(over)+" "+str(under)+" "+str(score_full))
						found = 1
						game_dup.append(kkk)
						break
			if found == 0:
				print "has not found any game"
				if mode == "half":
					fout.write(fin_line[0:len(fin_line)-1]+"#"+str(1.9)+" "+str(1.9)+" "+str(7.3)+" "+str(1.9)+" "+str(1.9)+" (0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0, 0:0)"+"\n")
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
