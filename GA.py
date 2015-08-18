__author__ = 'JAEMIN'
"""Genetic Algorithmn Implementation
"""
#!/usr/bin/python
from multiprocessing import Process,Value,Array,Lock,Queue,sharedctypes
import random
import os
import numpy as np
import threading
import time
import ctypes
import sys
class GeneticAlgorithm(object):
	def __init__(self, genetics):
		self.genetics = genetics
		pass
	def run(self):
		population = self.genetics.initial()
		EM  = 0
		while True:
			#			fits_pops = [ (fit_value,[Chromsome]), ...)
			#fits_pops = [(self.genetics.fitness(ch,EM),ch) for ch in population]
			fits_list = self.genetics.fitness(population,EM)
			fits_pops = []
			for ii in range(0,len(population)):
				fits_pops.append((fits_list[ii],population[ii]))
			if self.genetics.check_stop(fits_pops,EM):
				break
			population = self.next(fits_pops,EM)
			#			EM = 1 if EM == 0 else 0
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
if __name__ == "__main__":
	"""
	example: MLB_Analysis
	chromo = [h_a,h_b,h_c,h_d,odds_h,a_a,a_b,a_c,a_d,odds_a]
	all the chromosome is 0-1 range
	  limit = computation number
	  size  = population size
	"""
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
		def fitness(self,population,EM):
			# MLB team analysis goes here we calculate every game and outputs bank total budjet
			# greater is better
			argument = int(sys.argv[1])
			TrainDurat = 150
			ExecDurat = 150
			TrainStart = 1500
			pid_num = 10
			pop_len = len(population)/pid_num
			results_list = []
			for iterr in range(0,pop_len):
				random_args = [(random.randint(0,0),random.randint(0,TrainStart)) for ii in range(0,pid_num)]
				random_lists = []
				bet_cond = int(sys.argv[2])
				for ii in random_args:
					ii_1,ii_2 = ii
#					tmp_list = self.MLB_File_List[ii_1]
					random_lists.append([ii_2,ii_2+TrainDurat+ExecDurat])
				result_queue = Queue()
				pid_t = []
				for jjjj in range(0,len(random_lists)):
					pid_t.append(Process(target = Training, args =(result_queue,population[jjjj+iterr*pid_num],random_lists[jjjj],argument,TrainDurat,bet_cond,EM)))
				#			pid_t = [Process(target = Gene_Multiprocess_Shared, args =(result_queue,chromo,File_List,argument,TrainDurat,bet_cond,EM)) for File_List in random_lists]
				for pid_t_start in pid_t:
					pid_t_start.start()
				for pid_t_join in pid_t:
					pid_t_join.join()
				for kkkk in range(0,len(pid_t)):
					results_list.append(result_queue.get())
				for pid_t_ter in pid_t:
					pid_t_ter.terminate()
			"""
			new_results = 0.0
			for ii in results:
				if(ii < 0):
					new_results += ii
				else:
					 new_results += ii
			"""
			#				return new_results/len(random_lists)
			return results_list

		def check_stop(self, fits_populations,EM):
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
				if int(sys.argv[1]) == 3 and max_fig > 0.9:
					cnt += 1
				elif int(sys.argv[1]) == 2 and max_fig > 400:
					cnt += 1
				elif int(sys.argv[1]) == 1 and max_fig > 600:
					cnt += 1
				elif int(sys.argv[1]) == 0 and max_fig > 250:
					cnt += 1
				elif int(sys.argv[1]) == 4 and max_fig > 0.55 and max_fig < 1.00:
					cnt += 1
				elif int(sys.argv[1]) == 5 and max_fig > 10:
					cnt += 1
				elif int(sys.argv[1]) == 6 and max_fig > 0.15:
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
			if int(sys.argv[1]) == 3:
				if(max_fig > 0.55):
					fout.write(str(max_fig)+"\t[")
					for ii in np_max:
						fout.write(str(ii)+",")
					fout.write("]\n")
			elif int(sys.argv[1]) > 0:
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
	GeneticAlgorithm(MLB_Analysis("Hello")).run()
	pass

	def
	def __init__(self):
	pass


