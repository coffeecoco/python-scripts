#!/usr/bin/env python
#
import sys
try:
	import xmlrpclib
	import multiprocessing
except ImportError, e:
	print 'ImportError:', e
	sys.exit(1)

SATELLITE_URL = "http://satellite/rpc/api"
CREDENTIALS = open("/Users/sumit.goel/.credentials", "r")
try:
	LINE = ((CREDENTIALS.readline()).rstrip()).split(":")
	SATELLITE_LOGIN = LINE[0]
	SATELLITE_PASSWORD = LINE[1]
finally:
	CREDENTIALS.close()

CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

def ADD_SYSTEMS(ITEM):
	SYSTEMID = ITEM['id']
	SYSTEMNAME = ITEM['name']
	RUNNINGKERNEL = CLIENT.system.getRunningKernel(KEY,SYSTEMID)
#	print type(RUNNINGKERNEL), RUNNINGKERNEL, multiprocessing.current_process().name
	if isinstance(RUNNINGKERNEL, str):
		if RUNNINGKERNEL.startswith("2.6.32"):
			CLIENT.systemgroup.addOrRemoveSystems(KEY,"ALL_RHEL6_SYSTEMS",SYSTEMID,True)
		elif RUNNINGKERNEL.startswith("2.6.18"):
			CLIENT.systemgroup.addOrRemoveSystems(KEY,"ALL_RHEL5_SYSTEMS",SYSTEMID,True)
		elif RUNNINGKERNEL.startswith("2.6.9"):
			CLIENT.systemgroup.addOrRemoveSystems(KEY,"ALL_RHEL4_SYSTEMS",SYSTEMID,True)
	return

if __name__ == '__main__':
	ALLSYSTEMS = CLIENT.system.listSystems(KEY)
#	PSIZE = multiprocessing.cpu_count()
	P = multiprocessing.Pool(processes=1)
	P.map(ADD_SYSTEMS, ALLSYSTEMS)
	P.close()
	P.join()

CLIENT.auth.logout(KEY)
#
#EOF
