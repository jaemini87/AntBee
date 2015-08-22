__author__ = 'JAEMIN'
"""Genetic Algorithmn Implementation
"""
#!/usr/bin/python
from multiprocessing import Process,Value,Array,Lock,Queue,sharedctypes
import sqlite3 as sql
import random
import os
import numpy as np
import threading
import time
import ctypes
import sys
import math
class GeneticAlgorithm(object):
	def __init__(self, genetics):
		self.genetics = genetics
		pass
	def run(self,args_list):
		population = self.genetics.initial()
		EM  = 0
		argument,mode,predict_mode,EM_enable = args_list
		while True:
			#			fits_pops = [ (fit_value,[Chromsome]), ...)
			#fits_pops = [(self.genetics.fitness(ch,EM),ch) for ch in population]
			args_list = argument,mode,predict_mode,EM
			fits_list = self.genetics.fitness(population,args_list)
			fits_pops = []
			for ii in range(0,len(population)):
				fits_pops.append((fits_list[ii],population[ii]))
			if self.genetics.check_stop(fits_pops,EM):
				break
			population = self.next(fits_pops,EM)
			if EM_enable == 1:
				EM = 1 if EM == 0 else 0
			pass
		return population
	def next(self, fits,EM):
		parents_generator = self.genetics.parents(fits)
		size = len(fits)
		nexts = []
		while len(nexts) < size:
			parents = next(parents_generator)
			cross = random.random() < self.genetics.probability_crossover()
			children = self.genetics.crossover(parents,EM) if cross else parents
			for ch in children:
				mutate = random.random() < self.genetics.probability_mutation()
				nexts.append(self.genetics.mutation(ch,EM) if mutate else ch)
				pass
			pass
		return nexts[0:size]
	pass

class GeneticFunctions(object):
	def probability_crossover(self):
		r"""returns rate of occur crossover(0.0-1.0)"""
		return 1.0
	def probability_mutation(self):
		r"""returns rate of occur mutation(0.0-1.0)"""
		return 0.0
	def initial(self):
		r"""returns list of initial population"""
		return []
	def fitness(self, chromosome,EM):
		r"""returns domain fitness value of chromosome"""
		return len(chromosome)
	def check_stop(self, fits_populations,EM):
		r"""stop run if returns True
		- fits_populations: list of (fitness_value, chromosome)
		"""
		return False
	def parents(self, fits_populations):
		r"""generator of selected parents
		"""
		gen = iter(sorted(fits_populations))
		while True:
			f1, ch1 = next(gen)
			f2, ch2 = next(gen)
			yield (ch1, ch2)
			pass
		return
	def crossover(self, parents,EM):
		r"""breed children
		"""
		return parents
	def mutation(self, chromosome,EM):
		r"""mutate chromosome
		"""
		return chromosome
	pass
class MLB_Analysis(GeneticFunctions):
	def __init__(self,db_file,limit=2000,size=100,prob_crossover=0.9, prob_mutation=0.1,chromo_size = 28):
		self.db_file = db_file
		self.counter = 0
		self.limit = limit
		self.size = size
		self.chromo_size = chromo_size
		#				self.chromo_size = 17
		#self.chromo_size = 22*int(sys.argv[3])
		self.prob_crossover = prob_crossover
		self.prob_mutation = prob_mutation
		self.max_fig = -10000000.0
		self.min_fig = 	10000000.0
		self.avg_fig = 0.0
		"""
		self.MLB2012 = Gene_File_Parser_OU("mlb2012.txt.mid.rev")
		self.MLB2013 = Gene_File_Parser_OU("mlb2013.txt.mid.rev")
		self.MLB2014 = Gene_File_Parser_OU("mlb2014.txt.mid.rev")
		self.MLB_File_List = [self.MLB2012,self.MLB2013,self.MLB2014]
		"""
		pass
	# GeneticFunctions interface impls
	def probability_crossover(self):
		return self.prob_crossover
	def probability_mutation(self):
		return self.prob_mutation
	def initial(self):
		return [self.random_chromo() for j in range(self.size)]
	def fitness(self,population,args_list):
		# MLB team analysis goes here we calculate every game and outputs bank total budjet
		# greater is better
		argument,mode,predict_mode,EM = args_list
		TrainDurat = 150
		ExecDurat = 150
		TrainStart = 1500
		pid_num = 10
		pop_len = len(population)/pid_num
		results_list = []
		for iterr in range(0,pop_len):
			random_args = [(random.randint(0,0),random.randint(0,TrainStart)) for ii in range(0,pid_num)]
			random_lists = []
			for ii in random_args:
				ii_1,ii_2 = ii
#					tmp_list = self.MLB_File_List[ii_1]
				random_lists.append([ii_2,TrainDurat,ExecDurat,argument,mode,predict_mode,EM])
			result_queue = Queue()
			pid_t = []
			for jjjj in range(0,len(random_lists)):
				pid_t.append(Process(target = self.Training, args =(result_queue,population[jjjj+iterr*pid_num],random_lists[jjjj])))
			#			pid_t = [Process(target = Gene_Multiprocess_Shared, args =(result_queue,chromo,File_List,argument,TrainDurat,bet_cond,EM)) for File_List in random_lists]
			for pid_t_start in pid_t:
				pid_t_start.start()
			for pid_t_join in pid_t:
				pid_t_join.join()
			for kkkk in range(0,len(pid_t)):
				results_list.append(result_queue.get())
			for pid_t_ter in pid_t:
				pid_t_ter.terminate()
		return results_list

	def check_stop(self, fits_populations,args_list):
		argument,mode,predict_mode,EM = args_list

		fout = open(str(sys.argv[4]),'a')
		self.counter += 1
		sort_population = iter(reversed(sorted(fits_populations)))
		sort_population2 = iter((sorted(fits_populations)))
		cnt = 0
		self.avg_fig = 0.0
		self.max_fig = -100000
		self.min_fig = 	100000
		self.summ = 0.0
		for iii in range(0,len(fits_populations)):
			maxx = next(sort_population)
			max_fig,max_chromosome = maxx
			if(self.max_fig < max_fig):
				self.max_fig = max_fig
				self.max_chromosome = max_chromosome
			if(self.min_fig > max_fig and max_fig != 0.0):
				self.min_fig = max_fig
				self.min_chromosome = max_chromosome
			self.avg_fig += max_fig
			if max_fig != 0.0:
				self.summ += 1.0
			if int(argument) == 3 and max_fig > 0.9:
				cnt += 1
			elif int(argument) == 2 and max_fig > 400:
				cnt += 1
			elif int(argument) == 1 and max_fig > 600:
				cnt += 1
			elif int(argument) == 0 and max_fig > 250:
				cnt += 1
			elif int(argument) == 4 and max_fig > 0.55 and max_fig < 1.00:
				cnt += 1
			elif int(argument) == 5 and max_fig > 10:
				cnt += 1
			elif int(argument) == 6 and max_fig > 0.15:
				cnt += 1
		if self.summ != 0:
			ratio = 1.0*cnt/self.summ
			self.avg_fig = self.avg_fig/self.summ
		else:
			ratio = 0.0
			self.avg_fig = 0.0
		if  ratio > 0.8:
			print "Checked Stop"
			print ratio
			return 1
		#				fits = [f for f, ch in fits_populations]
		#				best = max(fits)
		np.set_printoptions(precision=3)
		np_max = np.array(self.max_chromosome)
		print("Max %.3f Min %.3f Avg %.3f")%(self.max_fig,self.min_fig,self.avg_fig)
		print ratio
		print(self.max_chromosome)
		print("%d---------------------------------------------------%d")%(EM,EM)
		print(np_max)
		if int(argument) == 3:
			if(max_fig > 0.55):
				fout.write(str(max_fig)+"\t[")
				for ii in np_max:
					fout.write(str(ii)+",")
				fout.write("]\n")
		elif int(argument) > 0:
			if(max_fig > 600):
				fout.write(str(max_fig)+"\t[")
				for ii in np_max:
					fout.write(str(ii)+",")
				fout.write("]\n")
			#				print(np_max)
		fout.close()
		#				for x in max_chromosome: print "%0.2f" % (x)
		if self.counter > self.limit:
			print(max_fig)
			#					print(np_max)
			return 1
		else:
			return 0
		"""
		self.counter += 1

		if self.counter % 10 == 0:
			best_match = list(sorted(fits_populations))[-1][1]
			fits = [f for f, ch in fits_populations]
			best = max(fits)
			worst = min(fits)
			ave = sum(fits) / len(fits)
			pass

		return self.counter >= self.limit
		"""
	def parents(self, fits_populations):
		while True:
			father = self.tournament(fits_populations)
			mother = self.tournament(fits_populations)
			yield (father, mother)
			pass
	pass
	def crossover(self, parents,EM):
		father, mother = parents
		child1 = []
		child2 = []
		"""
		for ii in range(0,self.chromo_size):
			if random.uniform(0.0,1.0) > 0.5:
				child1.append(father[ii])
				child2.append(mother[ii])
			else:
				child1.append(mother[ii])
				child2.append(father[ii])
		"""
		if EM == 0:
			CROSS_START = 1
			CROSS_END = 39
		else:
			CROSS_START = 40
			CROSS_END = 59
		index1 = random.randint(CROSS_START, CROSS_END)
		index2 = random.randint(CROSS_START, CROSS_END)
		if index1 > index2:
			index1, index2 = index2, index1
		child1 = father[:index1] + mother[index1:index2] + father[index2:]
		child2 = mother[:index1] + father[index1:index2] + mother[index2:]

		return (child1, child2)
	def mutation(self, chromosome,EM):
		if EM == 0:
			MUT_START = 1
			MUT_END = 21
			MUT_END = 39
		else:
			MUT_START = 40
			MUT_END = 59
		index = random.randint(MUT_START,MUT_END)
		vary = random.uniform(0.0,1.0)
		#				vary = random.randint(0,1)
		mutated = list(chromosome)
		mutated[index] = vary
		return mutated
	# internals
	def tournament(self, fits_populations):
		alicef, alice = self.select_random(fits_populations)
		bobf, bob = self.select_random(fits_populations)
		return alice if alicef > bobf else bob
	def select_random(self, fits_populations):
		return fits_populations[random.randint(0, len(fits_populations)-1)]
	def random_chromo(self):
		return [random.uniform(0.0,1.0) for i in range(self.chromo_size)]
	#return [random.randint(0,1) for i in range(self.chromo_size)]
	pass


	def Training(self,result_queue,chromo,args_list):
		#db file open API insert
		#CODE HERE\
		#db file open API insert
		#args_list = [train start, train dur, exec end, argument(),bet_cond,EM] 6

		if len(args_list) == 6:
			db_file,train_start,train_dur,exec_end,args,mode,predict_mode,EM = args_list
		home_stats_avg = [0.0 for ii in range(0,14)]
		home_stats_std = [0.0 for ii in range(0,14)]
		away_stats_avg = [0.0 for ii in range(0,14)]
		away_stats_std = [0.0 for ii in range(0,14)]
		conn = sql.connect(db_file)
		cur = conn.cursor()
		cur.execute("select * from MLB_SU where nid>:nid_s and nid<:nid_e)",{"nid_s":train_start,"nid_e":exec_end})
		home_stats = []
		away_stats = []
		counter = 0.0
		for fin_line in cur:
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
			home_stats_avg += np.array(home_stats)
			away_stats_avg += np.array(away_stats)
			home_stats_std += np.array(home_stats)*np.array(home_stats)
			away_stats_std += np.array(away_stats)*np.array(away_stats)
			counter += 1.0
		home_stats_avg /= np.array(home_stats_avg)/counter
		away_stats_avg /= np.array(away_stats_avg)/counter
		home_stats_std /= np.array(home_stats_std)/counter
		away_stats_std /= np.array(away_stats_std)/counter
		home_stats_std = pow(np.array(home_stats_std)-np.array(home_stats_avg),0.5)
		away_stats_std = pow(np.array(away_stats_std)-np.array(away_stats_avg),0.5)

		Odds_ratio = 0.0
		Budjet = 200.0
		MinBudjet = Budjet
		MaxBudjet = 0
		Winmoney = Budjet/40
		Winmoney_incr = Winmoney/10
		Jaemin = Bank("Jaemin",Budjet)
		Jaemin.set_Winmoney(Winmoney)
	# TrainStart min is 1
	#rrrrrrrrrrrrr
		TrainStart = train_start
	# TrainDurat is now new argument
		TrainDurat = train_dur
		ExecDurat  = exec_end

		TrainCount = 0
		count_w = 0
		count_l = 0
		count_h = 0
		count_a = 0
		current_budjet = 200.0
		for fin_line in cur:
			if not fin_line:
				break
			TrainCount += 1
			if (TrainCount < TrainStart):
				continue
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
			home_stats = (np.array(home_stats)-np.array(home_stats_avg))/np.array(home_stats_std)
			away_stats = (np.array(away_stats)-np.array(away_stats_avg)/np.array(away_stats_std))
			home_chr_stats = np.array(home_stats)*np.array(chromo[0:14])
			away_chr_stats = np.array(away_stats)*np.array(chromo[14:28])

			if TrainCount > TrainStart+TrainDurat and TrainCount < TrainStart+TrainDurat+ExecDurat:
				home_away =  self.predict_game(home_chr_stats,away_chr_stats,predict_mode)
				if home_away == 1:
					count_h += 1
					bet_game = 1
				elif home_away == -1:
					count_a += 1
					bet_game = -1
				else:
					bet_game = 0
				#bet_game determination mppp
				if bet_game == 1:
					pay_out = Jaemin.get_Winmoney()
				elif bet_game == -1:
						pay_out = Jaemin.get_Winmoney()
				else :
					pay_out = 0
				correct_money = 0
	#	print("%d%d%d%d\n"%(hand_minus_home,hand_plus_home,hand_minus_away,hand_plus_away))
				if self.result_game(game_stats,mode,home_away) == bet_game:
					correct_money = self.odds_game(game_stats,mode,home_away)*pay_out
					count_w += 1
				elif bet_game == 0:
					correct_money = 0
				else :
					count_l += 1
					correct_money = 0
				Jaemin.buyin(correct_money)
				Jaemin.payout(pay_out)
			MinBudjet = min(MinBudjet,Jaemin.get_Budjet())
			MaxBudjet = max(MaxBudjet,Jaemin.get_Budjet())
		if count_w+count_l == 0:
			Odds_ratio = 0
		else:
			Odds_ratio += count_w/(count_w+count_l*1.0)
		argument_list_tmp = np.array([MinBudjet,MaxBudjet,Jaemin.get_Budjet(),Odds_ratio])
		result_queue.put(argument_list_tmp[args])

	def result_game(self,game_stats,mode,home_away):
		if mode == "money":
			if home_away == 1 and game_stats[8] != 0:
				return 1
			elif home_away == -1 and game_stats[9] != 0:
				return -1
			else :
				return 0
		elif mode == "run":
			if home_away == 1 and game_stats[10] != 0:
				return 1
			elif home_away == -1 and game_stats[11] != 0:
				return -1
			else :
				return 0
		elif mode == "ou":
			if home_away == 1 and game_stats[12] == 1:
				return 1
			elif home_away == -1 and game_stats[12] == -1:
				return -1
			else :
				return 0
		else:
			return 0
		pass
		season,day,month,year,time,team_h,team_a,su_h,su_a,run_h,run_a,ou,odds_h,odds_a,odds_o,odds_u,\
	def odds_game(self,game_stats,mode,home_away):
		if mode == "money":
			if home_away == 1:
				return game_stats[13]
			elif home_away == -1 :
				return game_stats[14]
			else :
				return 0
		elif mode == "run":
			if home_away == 1:
				return game_stats[13]*1.4
			elif home_away == -1 :
				return game_stats[14]*1.4
			else :
				return 0
		elif mode == "ou":
			if home_away == 1 :
				return game_stats[15]
			elif home_away == -1 :
				return game_stats[16]
			else :
				return 0
		else:
			return 0
		pass
	def predict_game(self,home_chr_stats,away_chr_stats,predict_mode):
		if predict_mode == "add":
			if sum(home_chr_stats)>sum(away_chr_stats):
				return 1
			else:
				return -1
		else:
			return 0
		pass

argument = sys.argv[1]
mode = "money"
predict_mode = "add"
EM_enable = 0
args_list = argument,mode,predict_mode,EM_enable
GeneticAlgorithm(MLB_Analysis("Hello")).run()
