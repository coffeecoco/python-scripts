#!/usr/bin/env python

__author__ = "Sumit Goel"

# Description: This script will pull the data from Red Hat Satellite
# and create a CSV file with the information.

import sys
try:
  import socket
  import xmlrpclib
  import getpass
  import time
  import csv
  import re
except ImportError, e:
  print 'ImportError:', e
  sys.exit(1)

DEFAULT_SERVER = socket.gethostname()
try:
  SATELLITE_SERVER = raw_input("Enter RedHat Satellite Server Name [%s]: " % DEFAULT_SERVER)
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
  print "Incorrect Server Name -", e
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
  print "You did not enter anything. You need to run the script again!"
  sys.exit(1)

CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
try:
  KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
  ALLSYSTEMS = CLIENT.system.listSystems(KEY)
except xmlrpclib.Fault, e:
  print 'xmlrpclib.Fault:', e
  sys.exit(1)

FILENAME = "rh_satellite_systems_dmi_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
FILEPATH = "/Users/sumit.goel/Downloads/" + FILENAME
OUTFILE = open(FILEPATH, 'wb')
CSVFILE = csv.writer(OUTFILE,quoting=csv.QUOTE_ALL)
CSVFILE.writerow(['Server Name','Vendor','Product','Asset','Serial'])

for ITEM in reversed(ALLSYSTEMS):
  SYSTEMID = ITEM['id']
  SYSTEMNAME = ITEM['name']
  try:
    SYSTEMDMI = CLIENT.system.getDmi(KEY,SYSTEMID)
    SERIALSTRING = SYSTEMDMI['asset'].replace('.', '')
    SERIALSTRING = SERIALSTRING.replace(' ', '')
    SERIALNUMBER = re.search(r'(system):([\w-]+)', SERIALSTRING)
    if SERIALNUMBER:
      SERIALNUMBER = SERIALNUMBER.group(2)
    else:
      SERIALNUMBER = re.search(r'(board):(\w+)', SERIALSTRING)
      if SERIALNUMBER:
        SERIALNUMBER = SERIALNUMBER.group(2)
      else:
        break
  except socket.error, e:
    print "socket.error:", e
    break
  except xmlrpclib.Fault, e:
    print "xmlrpclib.Fault:", e
    break
  except xmlrpclib.ProtocolError, e:
    print "xmlrpclib.ProtocolError:", e
    break
  try:
    CSVFILE.writerow([SYSTEMNAME, SYSTEMDMI['vendor'], SYSTEMDMI['product'], SYSTEMDMI['asset'], SERIALNUMBER])
  except csv.Error, e:
    print "Error:", e
    break

OUTFILE.close()

TECHASSETCSV = sys.argv[1] 

CLT.auth.logout(KEY)
#
#EOF
