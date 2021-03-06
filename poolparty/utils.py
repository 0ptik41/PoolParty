import client as cl
import socket
import string 
import random
import time
import sys 
import os 

VER = int(sys.version.split(' ')[0].split('.')[0])
if VER  < 3:
	charpool = list(string.lowercase + string.uppercase)
else:
	charpool = list(string.ascii_lowercase + string.ascii_uppercase)

def build_deps(libs):
	[os.system('pip install %s' % lib) for lib in libs]

def swap(f,d):
	out = []
	for ln in open(f,'r').readlines():
		out.append(ln.replace('\n', ''))
	if d:
		os.remove(f)
	return out 

def create_random_filename(ext):
	basename = ''.join(random.sample(charpool, 6))
	random_file = basename +ext
	return random_file

def cmd(command, verbose):
	tmp = create_random_filename('.sh')
	tmp2 = create_random_filename('.txt')
	data = '#!/bin/bash\n%s\n#EOF' % command
	open(tmp, 'w').write(data)
	os.system('bash %s >> %s' % (tmp,tmp2))
	os.remove(tmp)
	if verbose:	
		os.system('cat %s' % tmp2)
	return swap(tmp2, True)

def arr2str(content):
	result = ''
	for element in content:
		result += element + '\n'
	return result

def arr2chstr(content):
	result = ''
	for element in content:
		result += element + ' '
	return result

def create_timestamp():
    date = time.localtime(time.time())
    mo = str(date.tm_mon)
    day = str(date.tm_mday)
    yr = str(date.tm_year)

    hr = str(date.tm_hour)
    min = str(date.tm_min)
    sec = str(date.tm_sec)

    date = mo + '/' + day + '/' + yr
    timestamp = hr + ':' + min + ':' + sec
    return date, timestamp

def create_listener(port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('0.0.0.0', port))
		s.listen(5)
	except socket.error:
		print('[!] Unable to Create Listener')
		pass
	return s

def check_peer_file():
	found = True
	if not os.path.isfile('.peers'):
		print('[!] You dont have any peers')
		found = False
	return found

def load_peers():
	peers = open('.peers','rb').read().decode('utf-8').split('\n')
	peers.pop(-1)
	print('[*] %d Peers Found' % len(peers))
	return peers