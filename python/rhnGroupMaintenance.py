#!/usr/bin/env python
#
import sys
try:
#	import fileinput
	import xmlrpclib
	import socket
	import getpass
#	import os
#	import multiprocessing
#	import exceptions
#	import logging
except ImportError, e:
	print 'ImportError:', e
	sys.exit(1)

DEFAULT_SERVER = socket.gethostname()
print "....."
SATELLITE_SERVER = raw_input("RHN Satellite Server Hostname/IP Address [%s]: " % DEFAULT_SERVER)
if not SATELLITE_SERVER:
	SATELLITE_SERVER = DEFAULT_SERVER
	
try:
	SATELLITE_URL = "http://" + SATELLITE_SERVER + "/rpc/api"
	CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
	print "....."
	print "Red Hat Network Satellite Server version is %s" % CLIENT.api.systemVersion()
except socket.error as e:
	print "....."
	print "Incorrect Hostname/IP Address - ", e
	sys.exit(1)

DEFAULT_LOGIN = getpass.getuser()
print "....."
SATELLITE_LOGIN = raw_input("RHN Satellite Login Name [%s]: " % DEFAULT_LOGIN)
if not SATELLITE_LOGIN:
	SATELLITE_LOGIN = DEFAULT_LOGIN
SATELLITE_PASSWORD = getpass.getpass("Enter Your Password: ")
if not SATELLITE_PASSWORD:
	print "....."
	print "You did not enter anything, please start over!"
	sys.exit(1)

try:
	KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
	LOGIN_DETAILS = CLIENT.user.getDetails(KEY,SATELLITE_LOGIN)
	print "....."
	print "Autentication Successful. Welcome %s %s!" % (LOGIN_DETAILS.get("first_name"),LOGIN_DETAILS.get("last_name"))
except:
	print "....."
	print "Authentication failed! Please check your username/password and try again."
	print "....."
	sys.exit(1)

def MAIN_OPTIONS():
	print ""
	print "What would you like to do now?"
	print ""
	print "1. Do you want to list systems in a Group?"
	print "2. Do you want to add systems to a Group?"
	print "3. Do you want to remove systems from a Group?"
	print "4. Quit"
	print ""
	MAIN_INPUT = raw_input("Please enter your choice [1 2 3 4]: ")
	if MAIN_INPUT == "1":
		try:
			LIST_SYSTEMS()
		except:
			MAIN_OPTIONS()
	elif MAIN_INPUT == "2":
		try:
			ADD_SYSTEMS()
		except:
			MAIN_OPTIONS()
	elif MAIN_INPUT == "3":
		print "Work in progress"
		MAIN_OPTIONS()
	elif MAIN_INPUT == "4":
		print "....."
		print "Good Bye!"
		print "....."
		sys.exit(1)
	else:
		print "....."
		print "Incorrect input, please try again!"
		print "....."
		MAIN_OPTIONS()
		
def LIST_SYSTEMS():
	print "....."
	USER_INPUT = raw_input("Please enter Group name or leave it blank and hit enter to list all Groups: ")
	if not USER_INPUT:
		LIST = CLIENT.systemgroup.listAllGroups(KEY)
		for ITEM in LIST:
			print ITEM.get("name")
		LIST_SYSTEMS()
	else:
		try:
			LIST = CLIENT.systemgroup.listSystems(KEY,USER_INPUT)
		except xmlrpclib.Fault as e:
			print "....."
			print e
			print "....."
			print "There is no such Group, please try again!"
			print "....."
			MAIN_OPTIONS()
		if not LIST:
			print "....."
			print "This Group is empty."
			print "....."
			MAIN_OPTIONS()
		for ITEM in LIST:
			print ITEM.get("hostname")
		MAIN_OPTIONS()

def ADD_SYSTEMS():
	print "....."
	USER_INPUT_GROUP = raw_input("Please enter Group name or leave it blank and hit enter to list all Groups: ")
	if not USER_INPUT_GROUP:
		LIST = CLIENT.systemgroup.listAllGroups(KEY)
		for ITEM in LIST:
			print ITEM.get("name")
		ADD_SYSTEMS()
	USER_INPUT_HOSTNAME = raw_input("Enter the short hostname (multiple can be defined by comma seperated): ").split(",")
	if not USER_INPUT_HOSTNAME:
		print "....."
		print "You did not enter anything, please try again!"
		MAIN_OPTIONS()
	else:
		for INPUT in USER_INPUT_HOSTNAME:
			INPUT = INPUT.replace(" ", "")
			INPUT = INPUT.lstrip()
			INPUT1 = INPUT + ".internal.salesforce.com"
			SYSTEM = CLIENT.system.getId(KEY,INPUT1)
			if not SYSTEM:
				SYSTEM = CLIENT.system.getId(KEY,INPUT)
				if not SYSTEM:
					print "....."
					print "There is no such system, please try again!"
					ADD_SYSTEMS()
				else:
					SYSTEMID = SYSTEM[0]['id']
					RESPONSE = CLIENT.systemgroup.addOrRemoveSystems(KEY,USER_INPUT_GROUP,SYSTEMID,True)
					if RESPONSE == 1:
						print "....."
						print "%s has been successfully added to %s" % (INPUT,USER_INPUT_GROUP)
			else:
				SYSTEMID = SYSTEM[0]['id']
				RESPONSE = CLIENT.systemgroup.addOrRemoveSystems(KEY,USER_INPUT_GROUP,SYSTEMID,True)
				if RESPONSE == 1:
					print "....."
					print "%s has been successfully added to %s" % (INPUT1,USER_INPUT_GROUP)
		MAIN_OPTIONS()
			
MAIN_OPTIONS()		
CLIENT.auth.logout(KEY)
#
#EOF