#!/bin/bash
if [ $# -lt 1 ]; then
	echo 'Usage: '$0' [command]'
	exit
fi
mode=$1
test -f .peers
hasPeers=$(echo $?)
if [ $hasPeers -eq 1 ]; then
	echo '[!] Missing Peers'
	exit
fi
if [ $# -eq 1 ]; then 
	cat .peers | while read n; do
		python3 client.py $n $1
	done
fi
if [ $# -eq 2 ]; then 
	cat .peers | while read n; do
		python3 client.py $n $1 $2
	done
fi
#EOF
