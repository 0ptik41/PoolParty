import numpy as np
import hashlib
import random
import utils 
import os

def hashstring(msgin):
	h = hashlib.sha256()
	h.update(bytes(msgin))
	return h.digest()

def hashbins(hashval, nbins):
	binning = []
	if nbins > 32: nbins = 32
	chunksz = int(32/nbins)
	bins = np.array(range(0,len(hashval)+chunksz, chunksz))
	bins[1:] = bins[1:]-1
	i = 0
	for i in range(len(bins)):
		if i > 0:
			b = hashval[bins[i-1]:bins[i]]			
			binning.append(checksum(b))
		i += 1
	return binning

def checksum(hstring):
	total = 0
	for l in list(hstring):
		total += l
	return total

def distribute(file,nodes):
	hval = hashstring(open(file,'rb').read())
	bins = hashbins(hval, len(nodes))
	return nodes[np.nonzero(np.array(bins==np.max(bins),dtype=np.int))[0][0]]