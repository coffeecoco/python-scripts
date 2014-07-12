#!/usr/bin/env python
 
import sys
try:
  import fileinput
  import xmlrpclib
  import socket
  import getpass
  import os
except ImportError, e:
  print 'ImportError:', e
  sys.exit(1)
 
if len(sys.argv) == 1 or len(sys.argv) > 2:
  print "Usage: " + sys.argv[0] + " " + "serverlist\n\t where,\
  \b\b serverlist is the filename and filepath containing\
  \b\b the list of Satellite systems."
  sys.exit(1)
else:
  filesize = os.path.getsize(sys.argv[1])
  if filesize == 0:
    print "The " + sys.argv[1] + " file is empty. Please check\
    \b\b\b\b  the file and try again."
    sys.exit(1)
 
DEFAULT_SERVER = socket.gethostname()
SATELLITE_SERVER = raw_input("RHN Satellite Server Hostname/IP\
 Address [%s]: " % DEFAULT_SERVER)
if not SATELLITE_SERVER:
  SATELLITE_SERVER = DEFAULT_SERVER
 
DEFAULT_LOGIN = getpass.getuser()
SATELLITE_LOGIN = raw_input("RHN Satellite Login Name [%s]: " %\
 DEFAULT_LOGIN)
if not SATELLITE_LOGIN:
  SATELLITE_LOGIN = DEFAULT_LOGIN
 
def no_input(variable):
  if not variable:
    print "You did not enter anything. Please start over again!"
    sys.exit(1)
 
SATELLITE_PASSWORD = getpass.getpass("Enter Your Password: ")
no_input(SATELLITE_PASSWORD)
 
SATELLITE_URL = "http://" + SATELLITE_SERVER + "/rpc/api"
 
client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
 
def add_systems(groupname):
  for line in fileinput.input(sys.argv[1]):
    line = line.rstrip()
    if len(line) > 1:
      list = client.system.getId(key,line)
      if not list:
        print "%s >> System does not exists." % line
      else:
        for system in list:
          systemid = system.get('id')
          response = client.systemgroup.addOrRemoveSystems(key,\
          groupname,systemid,True)
          if response == 1:
            print "%s >> Success!" % line
          else:
            print "%s >> %s" % (line, response)

USER_INPUT = raw_input("Do you want to create new System Group? \
 [Yes/No] ")
if USER_INPUT == 'Yes' or USER_INPUT == 'YES' or USER_INPUT == 'yes':
  SYSTEM_GROUP_NAME = raw_input("Please enter System Group name: ")
  no_input(SYSTEM_GROUP_NAME)
  SYSTEM_GROUP_DESC = raw_input("Please enter System Group\
  description: ")
  no_input(SYSTEM_GROUP_DESC)
  client.systemgroup.create(key,SYSTEM_GROUP_NAME,SYSTEM_GROUP_DESC)
  list = client.systemgroup.getDetails(key,SYSTEM_GROUP_NAME)
  for group in list:
    print "The ID of System Group" + SYSTEM_GROUP_NAME + "is" +\
    group.get('id') + "."
    USER_CONFIRMATION = raw_input("Would you like to add the Systems\
    in this group now? [Yes/No] ")
    if USER_CONFIRMATION == 'Yes' or USER_CONFIRMATION == 'YES' or \
    USER_CONFIRMATION == 'yes':
      add_systems(SYSTEM_GROUP_NAME)
    else:
      print "Please run the script again to add the systems."
elif USER_INPUT == 'No' or USER_INPUT == 'NO' or USER_INPUT == 'no':
  list = client.systemgroup.listAllGroups(key)
  for group in list:
    print group.get('name')
  USER_INPUT_GROUP = raw_input("Please enter the System Group name\
  from the above list: ")
  no_input(USER_INPUT_GROUP)
  USER_CONFIRMATION = raw_input("Would you like to add the Systems in\
  this group now? [Yes/No] ")
  if USER_CONFIRMATION == 'Yes' or USER_CONFIRMATION == 'YES' or\
  USER_CONFIRMATION == 'yes':
    add_systems(USER_INPUT_GROUP)
  else:
    print "Please run the script again to add the systems."
  
client.auth.logout(key)
#EOF