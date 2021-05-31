import utils 
import json
import time 
import os 

class Node:
	
	def __init__(self):
		self.memory = self.check_memory()
		self.hostname = os.getlogin()
		self.os = os.name
		self.uptime = 0.0


	def check_memory(self):
		free_mem = utils.cmd('free --kilo',False)
		mem_labels = free_mem[0]
		mem_labels = list(filter(None,mem_labels.split(' ')))
		mem_free = list(filter(None,free_mem[1].split(' ')))
		mem_free.pop(0)
		memory_data = {}
		i = 0
		for label in mem_labels:
			memory_data[label] = mem_free[i]
			i += 1
		return memory_data

	def set_uptime(self,new_dt):
		self.uptime = new_dt
