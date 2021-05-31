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
	bins = np.array(range(0,len(hstr)+chunksz, chunksz))
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
		total += ord(l)
	return total
