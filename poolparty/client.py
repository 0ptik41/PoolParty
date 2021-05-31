try:
	from tqdm import tqdm
except ImportError:
	print('\033[31m[*] Missing tqdm\033[0m')
	pass
import socket
import utils
import time
import sys 
import os

def send_file(fname, rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sz = os.path.getsize(fname)
	packets = []
	if sz > 1024:
		npackets = int(sz/1024) 
		print('[-] Fragmenting file into %d packets' % npackets)
		with open(fname, 'rb') as f:
			while True:
				chunk = f.read(1024)
				if chunk == b'':
					break
				else:
					packets.append(chunk)
		f.close()
	else:
		npackets = 1
		packets.append(open(fname,'rb').read())
	print('[+] Attempting to send %d packets [%d bytes] to %s:%d' % (len(packets),sz, rhost, rport))
	qstr = 'Transfer :::: %s,%s' % (fname,npackets)
	s.connect((rhost,rport))
	s.send(qstr.encode('utf-8'))
	if s.recv(1024).decode('utf-8').find('OK'):
		progress = tqdm(total=len(packets))
		for p in packets:
			s.send(p)
			progress.update(1)
		progress.close()
		print('[+] Finished')
	else:
		print('[x] Share was rejected')
	time.sleep(1)
	s.close()

def delete_file(fname, rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	print('[+] Attempting to delete remote file %s' % fname)
	qstr = 'Delete :::: %s' % fname
	s.send(qstr.encode('utf-8'))
	deleted = s.recv(1024).decode('utf-8').find('[+]') >= 0
	s.close()
	return deleted

def list_files(rhost,rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ListFiles :::: Please?'
	s.send(qstr.encode('utf-8'))
	rmt_files = s.recv(1024).decode('utf-8')
	s.close()
	return rmt_files

def uptime(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'Uptime :::: Please?'
	s.send(qstr.encode('utf-8'))
	res = s.recv(1025).decode('utf-8') 
	s.close()
	return res

def check_memory(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ShowMemory :::: Please?'
	s.send(qstr.encode('utf-8'))
	res = s.recv(1024).decode('utf-8')
	s.close()
	return res

def list_peers(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ListPeers :::: Please?'
	s.send(qstr.encode('utf-8'))
	res = s.recv(1024).decode('utf-8')
	s.close()
	return res

def update_code(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'Update :::: Please?'
	s.send(qstr.encode('utf-8'))
	res = s.recv(1024).decode('utf-8')
	s.close()
	return res

def shutdown_peer(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'Shutdown :::: Now'
	s.send(qstr.encode('utf-8'))
	s.close()
	return True

def add_peer(peer_ip, rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'AddPeer :::: %s' % peer_ip
	s.send(qstr.encode('utf-8'))
	reply = s.recv(1025).decode('utf-8')
	print(reply); s.close()
	return reply.find('[+]')!=-1 

def file_hash(rfile, rhost, rport):
	print('[+] Checking %s hashsum for %s' % (rhost, rfile))
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'HashVal :::: %s' % rfile
	s.send(qstr.encode('utf-8'))
	res = s.recv(1024).decode('utf-8')
	s.close()
	return res

def usage():
	print('Usage: python test_client.py [mode]')
	print('Modes:')
	print(' -list-peers')
	print(' -list-files')
	print(' -memory')
	print(' -delete')
	print(' -send')
	print(' -update')
	exit()

def kill_all(nodes):
	results = {}
	for node in nodes:
		try:
			shutdown_peer(node, 4242)
			results[node] = True
		except:
			print('[!] %s may be offline' % node)
			results[node] = False
			pass
	return results

def check_uptimes(nodes):
	results = {}
	for node in nodes:
		try:
			results[node] = uptime(node, 4242)
		except:
			print('[!] %s may be offline' % node)
			results[node] = []
			pass
	return results



def main():
	rp = 4242
	# Check args in
	if len(sys.argv) > 2:
		rmt = sys.argv[1]

		if '-send' in sys.argv and os.path.isfile(sys.argv[3]):
			test_file = sys.argv[3]
			send_file(test_file,rmt,rp)

		if '-delete' in sys.argv:
			delete_file(sys.argv[3],rmt,rp)

		if '-list-files' in sys.argv:
			print(list_files(rmt, rp))

		if '-uptime' in sys.argv:
			print(uptime(rmt, rp))

		if '-memory' in sys.argv:
			print(check_memory(rmt, rp))

		if '-list-peers' in sys.argv:
			print(list_peers(rmt, rp))

		if '-update' in sys.argv:
			print(update_code(rmt, rp))

		if '-shutdown' in sys.argv:
			shutdown_peer(rmt, rp)

		if '-add-peer' in sys.argv:
			add_peer(sys.argv[3], rmt, rp)

		if '-hash' in sys.argv:
			print(file_hash(sys.argv[3], rmt, rp))

	elif '-kill-all' in sys.argv:
			if utils.check_peer_file():
				kill_all(utils.load_peers())
	else:
		usage()

if __name__ == '__main__':
	main()
