#!/usr/bin/env python
#
__author__ = 'Sumit Goel'

import sys
try:
  import socket
  import xmlrpclib
  import getpass
except ImportError, e:
  print 'ImportError:', e
  sys.exit(1)

def api():
  def server():
    DEFAULT_SERVER = socket.gethostname()
    try:
      SATELLITE_SERVER = raw_input('Enter RedHat Satellite Server Name [%s]: ' % DEFAULT_SERVER)
    except KeyboardInterrupt:
      print ""
      sys.exit(1)
    if not SATELLITE_SERVER:
      SATELLITE_SERVER = DEFAULT_SERVER
    try:
      SATELLITE_URL = 'http://' + SATELLITE_SERVER + '/rpc/api'
      CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
      print "Welcome to RedHat Satellite Server %s" % CLIENT.api.systemVersion()
    except socket.error, e:
      print "Incorrect Server Name -", e
      sys.exit(1)
    return CLIENT

  def username():
    DEFAULT_LOGIN = getpass.getuser()
    try:
      SATELLITE_LOGIN = raw_input("Enter RedHat Satellite Login Name [%s]: " % DEFAULT_LOGIN)
    except KeyboardInterrupt:
      print ""
      sys.exit(1)
    if not SATELLITE_LOGIN:
      SATELLITE_LOGIN = DEFAULT_LOGIN
    return SATELLITE_LOGIN

  def password():
    try:
      SATELLITE_PASSWORD = getpass.getpass("Enter Your Password: ")
    except KeyboardInterrupt:
      print ""
      sys.exit(1)
    if not SATELLITE_PASSWORD:
      print 'You did not enter anything. Good bye!'
      sys.exit(1)
    return SATELLITE_PASSWORD

  CLIENT = server()
  SATELLITE_LOGIN = username()
  SATELLITE_PASSWORD = password()
  try:
    KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
  except (xmlrpclib.Fault, xmlrpclib.ProtocolError), e:
    print e
    sys.exit(1)
  return (KEY, CLIENT)

#
#EOF
