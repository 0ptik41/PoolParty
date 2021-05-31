from threading import Thread
import server
import utils
import client
import time
import json
import sys 
import os


class ControlCenter:

	def __init__(self):
		# check for peer list
		if utils.check_peer_file():
			self.nodes = utils.load_peers()




def main():
	
	if '-serve' in sys.argv:
		# Start Server to query nodes 
		backend = server.Server()

	# Spin up Local Web server 
	
	# Open Browser view 

if __name__ == '__main__':
	main()
