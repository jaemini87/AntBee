__author__ = 'jaemin'
import os
import PyPDF2
import sys
def Parser(input_file):
	finmlb = open(input_file,'r')
	fin_line = finmlb.readline()
	str_league,str_year,pagenumber = fin_line.split("|")
	pagenumber = int(pagenumber)
	command = "mkdir "+ str_league+str_year
	os.system(command)
	print(command)
	start = 2
	for ii in range(start,pagenumber+1):
		outputpdf = "./"+str_league+str_year+"/"+str(ii)+".pdf"
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
							over = over_t
							under = under_t
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
			# print(fin_line)
			if not fin_line: break
			if fin_line.find("|") == 0 or fin_line.find("|") == 1:
				fin_en = 0
				break
			if fin_en == 1:
				found  = 0
				game_dup = []
				for kkk in game_over_under:
					team,score_h,score_a,ou,over,under = kkk
					score = str(score_h)+":"+str(score_a)
					dash = str(team).find("-")
					dash2 = fin_line.find("-")
					if len(fin_line) < 12 or fin_line.find("-") == -1:
						continue
					elif (fin_line[6:9] == team[0:3] and fin_line[dash2+2:dash2+5] == team[dash+2:dash+5]) \
						and fin_line.find(score) != -1:
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
Parser("mlb.txt")
