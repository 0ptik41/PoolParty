from threading import Thread
import server
import utils
import time
import json
import sys 
import os


def main():
	# Load Node Settings
	nodes = utils.load_nodes() 
	# Start Server to query nodes 
	backend = server.Server()
	# Sping up Local Web server 
	# Open Browser view 

if __name__ == '__main__':
	main()
