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
except ImportError, e:
  print 'ImportError:', e
  sys.exit(1)

DFT_SRV = socket.gethostname()
try:
  SAT_SRV = raw_input("Enter RedHat Satellite Server Name [%s]: " \
            % DFT_SRV)
except KeyboardInterrupt:
  print ""
  sys.exit(1)
if not SAT_SRV:
    SAT_SRV = DFT_SRV

try:
  SAT_URL = "http://" + SAT_SRV + "/rpc/api"
  CLT = xmlrpclib.Server(SAT_URL, verbose=0)
  print "Welcome to RedHat Satellite Server %s" % CLT.api.systemVersion()
except socket.error, e:
  print "Incorrect Server Name -", e
  print "Please run the script again."
  sys.exit(1)

DFT_LIN = getpass.getuser()
try:
  SAT_LIN = raw_input("Enter RedHat Satellite Login Name [%s]: " \
            % DFT_LIN)
except KeyboardInterrupt:
  print ""
  sys.exit(1)
if not SAT_LIN:
  SAT_LIN = DFT_LIN

try:
  SAT_PWD = getpass.getpass("Enter Your Password: ")
except KeyboardInterrupt:
  print ""
  sys.exit(1)
if not SAT_PWD:
  print "You did not enter anything. You need to run the script again!"
  sys.exit(1)

CLT = xmlrpclib.Server(SAT_URL, verbose=0)
try:
  KEY = CLT.auth.login(SAT_LIN, SAT_PWD)
  ALLSYSTEMS = CLT.system.listSystems(KEY)
except xmlrpclib.Fault, e:
  print 'xmlrpclib.Fault:', e
  sys.exit(1)

FNAME = "rh_satellite_systems_dmi" + time.strftime("%Y%m%d%H%M%S") + ".csv"
FPATH = "/tmp/" + FNAME
OFILE = open(FPATH, 'wb')
CSVFILE = csv.writer(OFILE,quoting=csv.QUOTE_ALL)
CSVFILE.writerow(['Server Name','Vendor','Product','Asset'])

for ITEM in reversed(ALLSYSTEMS):
  SYSID = ITEM['id']
  SYSNAME = ITEM['name']
  try:
    SYSDMI = CLT.system.getDmi(KEY,SYSID)
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
    CSVFILE.writerow([SYSNAME, SYSDMI['vendor'], SYSDMI['product'], \
    SYSDMI['asset']])
  except csv.Error, e:
    print "Error:", e
    break

CLT.auth.logout(KEY)
#
#EOF
