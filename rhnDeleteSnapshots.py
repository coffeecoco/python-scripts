#!/usr/bin/env python
#
# Description: Script to delete the system snapshots older than 30 days.
# Author: Sumit Goel <sumit.goel@salesforce.com>
# Date: 20140624 - Initial Draft
#

import sys
try:
	import xmlrpclib
	import socket
	import getpass
	import datetime
except ImportError, e:
	print 'ImportError:', e
	sys.exit(1)

DEFAULT_SERVER = socket.gethostname()
try:
	SATELLITE_SERVER = raw_input("Enter RedHat Satellite Server Hostname/IP Address [%s]: " % DEFAULT_SERVER)
except KeyboardInterrupt:
	print ""
	sys.exit(1)
if not SATELLITE_SERVER:
	SATELLITE_SERVER = DEFAULT_SERVER

try:
	SATELLITE_URL = "http://" + SATELLITE_SERVER + "/rpc/api"
	CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
	print "Welcome to RedHat Satellite Server %s" % CLIENT.api.systemVersion()
except socket.error, e:
	print "Incorrect Hostname/IP Address -", e
	print "Please run the script again."
	sys.exit(1)

DEFAULT_LOGIN = getpass.getuser()
try:
	SATELLITE_LOGIN = raw_input("Enter RedHat Satellite Login Name [%s]: " % DEFAULT_LOGIN)
except KeyboardInterrupt:
        print ""
        sys.exit(1)

if not SATELLITE_LOGIN:
	SATELLITE_LOGIN = DEFAULT_LOGIN

try:
	SATELLITE_PASSWORD = getpass.getpass("Enter Your Password: ")
except KeyboardInterrupt:
        print ""
        sys.exit(1)

if not SATELLITE_PASSWORD:
	print "You did not enter anything. Sorry but you need to run the script again!"
	sys.exit(1)

CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
try:
	KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
except xmlrpclib.Fault, e:
	print 'xmlrpclib.Fault:', e
	sys.exit(1)
ALLSYSTEMS = CLIENT.system.listSystems(KEY)
print "[%s] Captured the list of all systems.." % datetime.datetime.now()
print "....."

for ITEM in reversed(ALLSYSTEMS):
	SYSTEMID = ITEM['id']
	SYSTEMNAME = ITEM['name']
	print "[%s] Processing the request for %s" % (datetime.datetime.now(), SYSTEMNAME)
	STARTDATE = datetime.datetime.now()-datetime.timedelta(days=3650)
	ENDDATE = datetime.datetime.now()-datetime.timedelta(days=45)
	DATESTRUCT = {'startDate': xmlrpclib.DateTime(STARTDATE.utctimetuple()), 'endDate': xmlrpclib.DateTime(ENDDATE.utctimetuple())}
	try:
		SNAPSHOTS = CLIENT.system.provisioning.snapshot.deleteSnapshots(KEY, SYSTEMID, DATESTRUCT)
		print "[%s] Snapshots successfully deleted for system %s from %s to %s" % (datetime.datetime.now(), SYSTEMNAME, STARTDATE, ENDDATE)
		print "....."
	except KeyboardInterrupt:
		print "KeyboardInterrupted"
		break
	except socket.error, e:
		print "socket.error:", e
		break
	except xmlrpclib.Fault, e:
		print "xmlrpclib.Fault:", e
		print "....."
		continue
	except xmlrpclib.ProtocolError, e:
		print "xmlrpclib.ProtocolError:", e
		print "....."
		continue

CLIENT.auth.logout(KEY)

#
#EOF
