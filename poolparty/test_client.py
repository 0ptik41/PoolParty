from tqdm import tqdm
import socket
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
	time.sleep(1)
	s.close()

def delete_file(fname, rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	print('[+] Attempting to delete remote file %s' % fname)
	qstr = 'Delete :::: %s' % fname
	s.send(qstr.encode('utf-8'))
	deleted = s.recv(1024).decode('utf-8').find('[+]') >= 0
	return deleted

def list_files(rhost,rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ListFiles :::: Please?'
	s.send(qstr.encode('utf-8'))
	rmt_files = s.recv(1024).decode('utf-8')
	return rmt_files

def uptime(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'Uptime :::: Please?'
	s.send(qstr.encode('utf-8'))
	return s.recv(1025).decode('utf-8') 

def check_memory(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ShowMemory :::: Please?'
	s.send(qstr.encode('utf-8'))
	return s.recv(1024).decode('utf-8')

def list_peers(rhost, rport):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost, rport))
	qstr = 'ListPeers :::: Please?'
	s.send(qstr.encode('utf-8'))
	return s.recv(1024).decode('utf-8')

def usage():
	print('Usage: python test_client.py [mode]')
	print('Modes:')
	print(' -list-peers')
	print(' -list-files')
	print(' -memory')
	print(' -delete')
	print(' -send')
	exit()


def main():
	# Constants for Debuggin
	test_file = 'test.txt'
	rmt = '192.168.1.164'
	rp = 4242
	# Check args in
	if len(sys.argv) > 1:
		
		if '-send' in sys.argv and os.path.isfile(sys.argv[2]):
			test_file = sys.argv[2]
			send_file(test_file,rmt,rp)

		if '-delete' in sys.argv:
			delete_file(sys.argv[2],rmt,rp)

		if '-list-files' in sys.argv:
			print(list_files(rmt, rp))

		if '-uptime' in sys.argv:
			print(uptime(rmt, rp))

		if '-memory' in sys.argv:
			print(check_memory(rmt, rp))

		if '-list-peers' in sys.argv:
			print(list_peers(rmt, rp))
	else:
		usage()

if __name__ == '__main__':
	main()
