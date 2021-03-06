from threading import Thread 
from node import Node
import numpy as np
import random
import storage
import base64 
import socket
import base64
import client as c
import utils
import json
import time
import os 

class Server:

	def __init__ (self, port=4242):
		self.sdate, self.stime = utils.create_timestamp()
		self.actions = {'Shutdown': self.shutdown,
					    'Transfer': self.recv_file,
					    'Delete': self.delete_file,
					    'ListFiles': self.list_files,
					    'ListPeers': self.list_peers,
					    'Uptime': self.uptime,
					    'ShowMemory': self.show_memory_usage,
					    'Update': self.update_code,
					    'AddPeer': self.add_peer,
					    'HashVal': self.give_hash}
		self.start = time.time()
		self.create_logfile()
		self.inbound = port
		self.running = True
		self.pool = []
		if os.path.isfile('.peers'):
			for p in utils.load_peers():
				self.pool.append(p)
		self.node = Node(self.pool)
		self.run()

	def create_logfile(self):
		# Make logging directory 
		if not os.path.isdir(os.getcwd()+'/.log'):
			os.mkdir('.log')
		# use time stamp to make logfile name
		f = self.sdate.replace('/','')+'_'+self.stime.replace(':','')
		self.logfile = os.getcwd()+'/.log/%s.log' % f
		open(self.logfile,'w').write('[*] Server Started %s - %s\n' %\
		 	(self.sdate, self.stime))

	def shutdown(self, s, a):
		print('\033[1m\033[31m[-] Shutting Down Server\033[0m')
		open(self.logfile,'w').write('[-] Shutting Down Server %s - %s' %\
		 	(self.sdate, self.stime))
		self.running = False
		return s


	def distribute_peer_list(self):
		mine = utils.cmd('hostname -I',False).pop().split(' ')[0]
		for node in self.pool:
			other_nodes = []
			random.shuffle(self.pool)
			for other in self.pool:
				time.sleep(np.random.randint(1,10,1)[0]/10)
				if other != node and node != mine:
					print('[>] Telling %s about %s' % (node, other)) 
					# Thread(target=c.add_peer, args=(other, node, 4242)).start()
					try:
						c.add_peer(other,node,4242)
					except socket.error:
						print('[!] Error adding peer')
						pass
	
		


	def run(self):
		sock = utils.create_listener(self.inbound)
		print('[+] Joining Pool \t|| %s - %s||' % (self.sdate, self.stime))
		self.node.set_uptime(time.time() - self.start)
		self.node.update_shares()
		iteration = 0
		try:
			while self.running:
				random.shuffle(self.pool)
				# Listen for incoming clients 
				try:
					client, info = sock.accept()
					# handle clients
					client = self.client_handler(client,info)
					client.close()
					# update shares 
					self.distribute_peer_list()
					self.node.distribute_shared_files()

					if iteration >1 and iteration%5==0:
						# check memory usage of other nodes and if they arent
						# able to be connected to, remove from pool
						for peer in self.pool:
							try:
								s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
								s.connect((peer, 4242))
								if not s.recv(1024).decode('utf-8').find('[-]'):
									self.pool.remove(peer)
							except socket.error:
								print('[!] Unable to reach %s. Removing from pool' % peer)
								self.pool.remove(peer)


				except socket.error:
					pass
				iteration += 1
		except KeyboardInterrupt:
			self.shutdown([],[],)
			pass

	def recv_file(self, sock, args):
		fname = args[0].replace('./','').split('/')[-1]
		npackets = int(args[1])
		if not os.path.isdir('received'):
			os.mkdir('received')
			os.mkdir('.shares/')
		if not os.path.isfile('received/%s'%fname):
			sock.send(b'[+] Send File OK')
			print('[-] Attempting to download file %s' % fname)
			print('[o] Begin receiving %d packets' % npackets)
			data = list(); 
			while len(data)<npackets:
				packet = sock.recv(2048).decode('utf-8')
				data.append(packet)
			open('received/%s' % fname,'wb').write(''.join(data).encode('utf-8'))
			sz = os.getsize('received/%s' % fname)
			print('[+] Done. Saving Data [%d bytes]' % sz)
		else:
			print(b'[x] Declining to receive %s' % fname)
			sock.send(b'[!] File Already Exists')
		return sock

	def delete_file(self, sock, args):
		fname = args[0]
		if not os.path.isfile(fname):
			sock.send(b'[x] Cannot find %s' % fname)
		else:
			print('[-] %s was requested to be deleted' % fname)
			os.remove(fname)
			sock.send(b'[+] %s was deleted' % fname)
		return sock

	def give_hash(self, sock, args):
		fname = args[0]
		if fname not in self.node.shares.keys():
			hdata = json.dumps(self.node.shares).encode('utf-8')
			sock.send(b'[x] Unknown File. Here are my hashes:\n'+hdata)
			print(self.node.shares.values())
		else:
			print(self.node.shares[fname])
			sock.send(bytes(self.node.shares[fname]))
		return sock

	def update_code(self, sock, args):
		os.system('git fetch')
		sock.send(b'[+] Latest code pulled from git repo')
		return sock

	def list_files(self, sock, args):
		shares = []
		if os.path.isdir('received'):
			for f in os.listdir('received'):
				shares.append('received/%s'%f)
		if os.path.isdir('shares'):
			for s in os.listdir('.shares'):
				shares.append('shared/%'%s)
		if os.path.isdir('.log'):
			for l in os.listdir('.log/'):
				shares.append('log/%s' % l)
		result = '\n'.join(shares)
		sock.send(result.encode('utf-8'))
		print('[-] Shared File List')
		return sock
	
	def uptime(self, sock, args):
		dt = time.time() - self.start
		ut = '[-] Uptime: %d seconds' % dt
		sock.send(ut.encode('utf-8'))
		self.node.set_uptime(dt)
		return sock

	def show_memory_usage(self, sock, args):
		data = json.dumps(self.node.check_memory())
		sock.send(data.encode('utf-8'))
		return sock

	def list_peers(self, sock, args):
		result = '\n'.join(self.pool)
		sock.send(result.encode('utf-8'))
		return sock

	def add_peer(self, sock, args):
		addr = args[0]
		if addr not in self.pool:
			self.pool.append(addr)
			print('[+] Adding %s to pool' % addr)
			sock.send(b'[+] Peer Added')
		else:
			sock.send(b'[x] Peer Known')
		return sock

	def client_handler(self, client, info):
		# Get Request 
		raw_request = client.recv(1024).decode('utf-8')
		print('[o] Connection Acccepted from %s:%d' % (info[0],info[1]))
		try:
			try:
				api_fc = raw_request.split(' :::: ')[0]
				params = raw_request.split(' :::: ')[1].split(',')
				if api_fc in self.actions.keys():
					client = self.actions[api_fc](client, params)
					# successful api actions get this client added as peer
					self.pool.append(info[0])
					self.pool = list(set(self.pool))
				else:
					print('Unknown request: %s' % raw_request)
			except IndexError:
				print('[!] Malformed API Request')
				pass
			
		except:
			print('Bad Request: %s' % raw_request)
			client.send(b'[!] Unable to process request')
			pass
		return client