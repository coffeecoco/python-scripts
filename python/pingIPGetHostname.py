#!/usr/bin/env python

__author__ = "Sumit Goel"
__email__ = "sumit.goel@outlook.com"

# Description: http://goo.gl/Ia8qzz
#

import sys
try:
	import subprocess
	import socket
	import getopt
	import multiprocessing
	import fileinput
except ImportError, e:
	print 'ImportError:', str(e)
	sys.exit(1)

def usage():
	print sys.argv[0] + ': missing argument'
	print 'Try \'' + sys.argv[0] + ' --help\' for more options.'

if len(sys.argv) == 1:
	usage()
	sys.exit(1)

def ping_host(host):
	host = host.lstrip()
	host = host.rstrip()
	host = host.replace(" ", "")
	try:
		RESPONSE = subprocess.call('ping -c 1 %s' % host, shell=True, stdout = open('/dev/null', 'w'), stderr=subprocess.STDOUT)
	except:
		print "Unspecified Error"
	if RESPONSE == 0:
		try:
			OUPUT = socket.gethostbyaddr(host)
			print '%s is Alive and hostname is %s' % (host, OUPUT[0])
		except:
			print '%s is Alive but hostname could not be resolved. Attention!!!' % host
	elif RESPONSE == 2: 
		print '%s: Did not respond. Attention!!!' % host
	elif RESPONSE == 68:
		print '%s: Could not resolve address. Attention!!!' % host
	else:
		print '%s: May be dead, Unspecified Error. Attention!!!' % host

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:f:", ["help", "ip-address=", "filename="])
	except getopt.GetoptError, e:
		print "GetoptError:", str(e)
		usage()
		sys.exit(1)
	for o, a in opts:
		if o in ("-h", "--help"):
			print 'Usage: ' + sys.argv[0] + ' [ -i ip-address] [ -f filename]'
			sys.exit()
		elif o in ("-i", "--ip-address"):
			IPADDRESS = a
			try:
				ping_host(IPADDRESS)
			except:
				print 'Unspecified Error'
		elif o in ("-f", "--filename"):
			FILENAME = a
			IPLIST = fileinput.input(FILENAME)
			if __name__ == '__main__':
				PSIZE = multiprocessing.cpu_count() * 4
				P = multiprocessing.Pool(processes=PSIZE)
				P.map(ping_host, IPLIST)
				P.close()
				P.join()
		else:
			assert False, "Unhandled Option"

if __name__ == "__main__":
	main()
