from threading import Thread
import utils 
import json
import time 
import os 

class Node:
	inbound = 2424
	def __init__(self, peers):
		self.memory = self.check_memory()
		self.hostname = os.getlogin()
		self.os = os.name
		self.uptime = 0.0
		self.running = True
		# get file hashes of shares 
		self.shares = self.setup_shares()
		self.serve = Thread(self.run_backend, ())
		self.serve.setDaemon(True)
		self.serve.start()

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

	def setup_shares(self):
		hashes = {}
		if not os.path.isdir('.shares/'):
			os.mkdir('.shares')
		if not os.path.isdir('received'):
			os.mkdir('received')
		else:
			# os.system('mv received/* .shares/')
			for f in os.listdir('received/'):
				fn = '%s/received/%s' % (os.getcwd(), f)
				fhash = utils.cmd('sha256sum %s' % fn,False).pop().split(' ')[0]
				hashes[fn] = fhash
			for fl in os.listdir('.shares'):
				fn = '%s/.shares/%s' % (os.getcwd(), fl)
				fhash = utils.cmd('sha256sum %s' % fn,False).pop().split(' ')[0]
				hashes[fn] = fhash
		return hashes

	def update_shares(self):
		self.shares = self.setup_shares()
		print('[-] %d shared files ' % len(self.shares.keys()))

	def run_backend(self):
		print('[-] Backend Server Listening on 0.0.0.0:%d'%self.backend)
		s = utils.create_listener(self.backend)
		iteration = 0
		try:
			while self.running:
				try:
					c, i = s.accept()
					c = self.handler(c,i)
					c.close()
				except socket.error:
					print('[!!] Connection error with %s' % i)
					pass
				iteration += 1
		except KeyboardInterrupt:
			self.running = False
			pass

	def handler(self, c, i):
		request = c.recv(1024).decode('utf-8')
		try:
			api_req = request.split(' :::: ')[0]
			params = request.split(' :::: ')[1].split(',')
			if api_req in self.actions.keys():
				c = self.actions[api_req](c, params)
		except IndexError:
			pass
		return c