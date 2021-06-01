from threading import Thread
import socket
import utils 
import json
import time 
import os 

class Node:
	inbound = 2424
	def __init__(self, peers):
		self.pool = peers
		self.actions = {'AddPeer': self.add_peer}
		self.memory = self.check_memory()
		self.hostname = os.getlogin()
		self.os = os.name
		self.uptime = 0.0
		self.running = True
		# get file hashes of shares 
		self.shares = self.setup_shares()
		serve = Thread(target=self.run_backend, args=())
		serve.setDaemon(True)
		serve.start()

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
		print('[-] Backend Server Listening on 0.0.0.0:%d'%self.inbound)
		s = utils.create_listener(self.inbound)
		iteration = 0
		try:
			while self.running:
				try:
					c, i = s.accept()
					c = self.handler(c,i)
					c.close()
					# update shares 
					self.shares = self.setup_shares()
					# check if peers have the same shares
				except socket.error:
					print('[!!] Connection error with %s' % i)
					pass
				iteration += 1
		except KeyboardInterrupt:
			self.running = False
			pass

	def add_peer(self, sock, args):
		addr = args[0]
		if addr not  in self.pool:
			self.pool.append(addr)
			print('[+] Added peer %s' % addr)
			sock.send(b'[+] Peer Added')
		else:
			sock.send(b'[x] Peer is known')
		return sock

	def hashdump(self, sock, args):
		hdata = json.dump(self.shares).encode('utf-8')
		sock.send(b'%s' % hdata)
		return sock

	def distribute_shared_files(self):
		for peer in self.pool:
			# Get files from this peer
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect((peer, 4242))
			s.send(b'HashVal :::: null')
			rmt_files = json.loads(s.recv(2048).encode('utf-8'))
			for rf in rmt_files:
				rhash = rmt_files[rf]
				if rhash not in self.shares.values():
					print('[o] %s has a file I dont [%s]'%(peer,rf))
			s.close()

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