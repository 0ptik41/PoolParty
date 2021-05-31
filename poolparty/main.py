from threading import Thread
import server
import utils
import client
import time
import json
import sys 
import os

def check_uptimes(nodes):
	results = {}
	for node in nodes:
		try:
			results[node] = client.uptime(node, 4242)
		except:
			print('[!] %s may be offline' % node)
			results[node] = []
			pass
	return results

def kill_all(nodes):
	results = {}
	for node in nodes:
		try:
			client.shutdown_peer(node, 4242)
			results[node] = True
		except:
			print('[!] %d may be offline' % node)
			results[node] = False
			pass
	return results

def main():
	# check for peer list
	if utils.check_peer_file():
		nodes = utils.load_peers()
		print(check_uptimes(nodes))
	
	# Start Server to query nodes 
	# backend = server.Server()

	# Spin up Local Web server 
	
	# Open Browser view 

if __name__ == '__main__':
	main()
