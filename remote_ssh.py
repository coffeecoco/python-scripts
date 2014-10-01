#!/usr/bin/env python
#
# Filename: remote_ssh.py
#
# Author: Sumit Goel (hello@sumitgoel.me)
#
# This script is created to run sudo command on remote servers where
# SSH to root is not allowed. It uses regular user credentials for
# authentication who has sudo privileges.
#
# This script is distrubuted in the hope that it will be useful,
# but WITHOUT ANY WARRANTY.
#
#

import sys

try:
    import paramiko
    import getpass
    import fileinput
    import time
    import argparse
    import subprocess
except ImportError, e:
    print 'ImportError:', e
    sys.exit(1)

parser = argparse.ArgumentParser(description="This script is created to run \
                                 sudo command on remote servers where SSH to \
                                 root is not allowed. It uses regular user \
                                 credentials for authentication who has sudo \
                                 privileges.", epilog="Cheers!!")

parser.add_argument('username', help='Specify your login name')

parser.add_argument('filename', help='Specify the file name and file path \
                    contaning the list of servers and ensure that the server \
                    names are listed in one column or per line')

parser.add_argument('command', help='Specify the command you want to run on \
                    remote server with sudo privileges (example: "grep root \
                    /etc/sudoers")')

parser.add_argument('-p', metavar='Port', dest='sshport', default=22, \
                	help='Specify the SSH port (default: 22)')

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

password = getpass.getpass("Enter Your Password: ")

def ping_host(host):
    ret = subprocess.call("ping -c 1 %s" % host, shell=True, \
                          stdout=open('/dev/null', 'w'), \
                          stderr=subprocess.STDOUT)
    if ret == 0:
        print "%s: is alive" % host
        try:
            manual_auth(line, int(args.sshport), args.username, password, \
                        args.command)
        except paramiko.SSHException, e:
            print 'SSHException:', e

    elif ret == 2:
        print "%s: did not respond" % host
    elif ret == 68:
        print "%s: couldn't resolve address" % host
    else:
        print "%s: unspecified error"

def manual_auth(h,p,u,pw,c):
    # Uncomment the next line to send paramiko logs to a logfile
    # paramiko.util.log_to_file('paramiko.log', level=10)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "Trying to connect %s now..." % h
    client.connect(h, p, u, pw, timeout=10)
    chann = client.invoke_shell()
    time.sleep(2)
    chann.send('sudo su -\n')
    time.sleep(4)
    chann.send('%s\n' % pw)
    time.sleep(2)
    chann.send('%s\n' % c)
    time.sleep(2)
    print chann.recv(65536)
    chann.close()
    client.close()

for line in fileinput.input([args.filename]):
    line = line.rstrip()
    if len(line) > 1:
        ping_host(line)

#
#EOF
