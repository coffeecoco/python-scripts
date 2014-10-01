#!/usr/bin/env python

__author__ = "Sumit Goel"

# Description: This script will pull the data from Red Hat Satellite
# and create a CSV file with the information.

## Required modules ##
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
## End ##

## Argument check ##
if len(sys.argv) == 1:
  print sys.argv[0] + ': missing argument'
  print 'Please pass the CSV file as an argument.'
  sys.exit(1)
## End ##

# Path to read and write CSV files
CSVPATH = '/Users/sumit.goel/Downloads/TechAssets/'

## Formatting CSV File ##
with open(sys.argv[1], 'rU') as ASSET_CSV_OPEN:
  ASSET_CSV_READER = csv.reader(ASSET_CSV_OPEN,delimiter=',')

  ASSET_CSV_FORMAT_FILE = CSVPATH + 'asset_formatted_' + time.strftime("%Y%m%d%H%M%S") + '.csv'
  ASSET_CSV_FORMAT_OPEN = open(ASSET_CSV_FORMAT_FILE, 'wb')
  ASSET_CSV_FORMAT_WRITER = csv.writer(ASSET_CSV_FORMAT_OPEN,delimiter=',',quoting=csv.QUOTE_ALL)
  ASSET_CSV_FORMAT_WRITER.writerow(next(ASSET_CSV_READER))

  for row in ASSET_CSV_READER:
    if len(row) > 2:
      ASSET_CSV_FORMAT_WRITER.writerow(row)

ASSET_CSV_OPEN.close()
ASSET_CSV_FORMAT_OPEN.close()
## END ##

## Request Red Hat Satellite Server Name ##
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
## END ##

## Request Satellite Server Login Name ##
DEFAULT_LOGIN = getpass.getuser()

try:
  SATELLITE_LOGIN = raw_input("Enter RedHat Satellite Login Name [%s]: " % DEFAULT_LOGIN)
except KeyboardInterrupt:
  print ""
  sys.exit(1)

if not SATELLITE_LOGIN:
  SATELLITE_LOGIN = DEFAULT_LOGIN
## END ##

## Request Login Password ##
try:
  SATELLITE_PASSWORD = getpass.getpass("Enter Your Password: ")
except KeyboardInterrupt:
  print ""
  sys.exit(1)

if not SATELLITE_PASSWORD:
  print "You did not enter anything. You need to run the script again!"
  sys.exit(1)
## END ##

## Initiate Satellite API connection and fetch all active systems ##
CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
try:
  KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
  ALLSYSTEMS = CLIENT.system.listSystems(KEY)
except xmlrpclib.Fault, e:
  print 'xmlrpclib.Fault:', e
  sys.exit(1)
## END ##

## Read asset formatted CSV file and create dictionary of hostnames ##
ASSET_CSV_OPEN = open(ASSET_CSV_FORMAT_FILE, 'rb')
ASSET_CSV_READER = csv.reader(ASSET_CSV_OPEN,delimiter=',')
ASSET_HOST_INDICES = dict((r[2], i) for i, r in enumerate(ASSET_CSV_READER))
ASSET_CSV_OPEN.close()
## END ##

## Create Uploadable Data Loader Insert CSV file with header##
DATA_LOADER_INSERT_FILE = CSVPATH + 'data_loader_insert_' + time.strftime("%Y%m%d%H%M%S") + '.csv'
DATA_LOADER_INSERT_OPEN = open(DATA_LOADER_INSERT_FILE, 'wb')
DATA_LOADER_INSERT_WRITER = csv.writer(DATA_LOADER_INSERT_OPEN,delimiter=',',quoting=csv.QUOTE_ALL)
DATA_LOADER_INSERT_WRITER.writerow(['HOST_NAME__C','STATE__C','SERIAL_NUMBER__C','OWNING_DEPARTMENT_CODE__C', \
'SERVICE__C','RECORDTYPEID','NAME'])
## END ##

## For each system in the satellite find the serial number then decide type (virtual or physical) ##
## Look for the system in assets csv and if not present then insert the row in uploadable data loader csv ##
for ITEM in reversed(ALLSYSTEMS):
  SYSTEMID = ITEM['id']

  SYSTEMNAME = ITEM['name']
  SYSTEMNAME = SYSTEMNAME.replace('.internal.salesforce.com','')
  SYSTEMNAME = SYSTEMNAME.replace('.adstage.salesforce.com','')

  SYSTEMDMI = CLIENT.system.getDmi(KEY,SYSTEMID)

  SERIALSTRING = SYSTEMDMI['asset'].replace('.', '')
  SERIALSTRING = SERIALSTRING.replace(' ', '')

  SERIALNUMBER = re.search(r'(system):([\w-]+)', SERIALSTRING)
  if SERIALNUMBER:
    SERIALNUMBER = SERIALNUMBER.group(2)
    if SERIALNUMBER.startswith('VMware-'):
      SERIALNUMBER = SERIALNUMBER.replace('VMware-', '')
      RECORDTYPE = '01270000000Dvhd'  #virtual
    else:
      RECORDTYPE = '01270000000Dvhc'  #physical
  else:
    continue

  ASSETNAME = SYSTEMNAME + '-' + SERIALNUMBER

  INDEX = ASSET_HOST_INDICES.get(SYSTEMNAME) #system lookup
  if INDEX is None:
    DATA_LOADER_INSERT_WRITER.writerow([SYSTEMNAME,'On',SERIALNUMBER,'935 - IT - Infrastructure and Operations', \
    'a2H700000004OipEAE',RECORDTYPE,ASSETNAME])

DATA_LOADER_INSERT_OPEN.close()
## END ##

## Create a dictionary of Satellite systems and look for systems in Satellite ##
SATELLITE_SYSTEM_DICT = dict((r['name'],i) for i, r in enumerate(ALLSYSTEMS))

DATA_LOADER_UPDATE_FILE = CSVPATH + 'data_loader_update_' + time.strftime("%Y%m%d%H%M%S") + '.csv'
DATA_LOADER_UPDATE_OPEN = open(DATA_LOADER_UPDATE_FILE, 'wb')
DATA_LOADER_UPDATE_WRITER = csv.writer(DATA_LOADER_UPDATE_OPEN,delimiter=',',quoting=csv.QUOTE_ALL)
DATA_LOADER_UPDATE_WRITER.writerow(['RECORDTYPEID','STATE__C','HOST_NAME__C','OPERATING_SYSTEM__C','STAGE__C', \
'CPU__C','RAM__C','IP_ADDRESS_1__C','SERIAL_NUMBER__C','SERVICE__C','OWNING_DEPARTMENT_CODE__C','NAME','Id'])

ASSET_CSV_OPEN = open(ASSET_CSV_FORMAT_FILE, 'rb')
ASSET_CSV_READER = csv.reader(ASSET_CSV_OPEN,delimiter=',')
next(ASSET_CSV_READER)
for row in ASSET_CSV_READER:
  INDEX = SATELLITE_SYSTEM_DICT.get(row[2])
  if INDEX is None:
    ASSET_HOSTNAME = row[2] + '.internal.salesforce.com'
    INDEX = SATELLITE_SYSTEM_DICT.get(ASSET_HOSTNAME)
    if INDEX is None:
      ASSET_HOSTNAME = row[2] + '.adstage.salesforce.com'
      INDEX = SATELLITE_SYSTEM_DICT.get(ASSET_HOSTNAME)
      if INDEX is None:
        DATA_LOADER_UPDATE_WRITER.writerow(row)

DATA_LOADER_UPDATE_OPEN.close()
ASSET_CSV_OPEN.close()
## END ##

## Closing the Satellite API connection 
CLIENT.auth.logout(KEY)

#
#EOF
