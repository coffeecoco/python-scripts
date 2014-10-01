#!/usr/bin/env python

# Author: Sumit Goel
# Description: A python program to gather system configuration,
#       tagging in Satellite for roll back if needed and then
#       actually applying all the applicable patches.

import sys
try:
    import socket
    import xmlrpclib
    import getpass
    import datetime
except ImportError, e:
    print 'ImportError:', e
    sys.exit(1)
    
pre_patch_script = '''
#!/bin/sh
echo "##### uptime #####"
uptime
'''

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def satellite_server():
    ''' This function will request the user to enter the Red Hat Satellite
    server name and try to make a connection if that's the correct server
    name.
    '''
    default_server = socket.gethostname()
    # satellite server name request
    inp_server = raw_input('Enter RedHat Satellite Server Name [%s]: ' % \
            default_server)
    if not inp_server:
        inp_server = default_server
    server_url = 'http://' + inp_server + '/rpc/api'
    try:
        # verify if satellite server is reachable
        client = xmlrpclib.Server(server_url, verbose=0)
        print 'Welcome to RedHat Satellite Server %s' % \
                client.api.systemVersion()
    except socket.error, e:
        print 'Incorrect Server Name -', e
        sys.exit(1)
    return client

def satellite_creds():
    ''' This function is used to request the satellite login name and
    password for authentication.
    '''
    default_login = getpass.getuser()
    # login name request
    inp_login = raw_input('Enter RedHat Satellite Login Name [%s]: ' % \
            default_login)
    if not inp_login:
        inp_login = default_login
    # password request
    inp_passwd = getpass.getpass('Enter Your Password: ')
    if not inp_passwd:
        print 'You did not enter anything. Please start over!'
        sys.exit(1)
    return (inp_login, inp_passwd)

def satellite_auth(client, inp_login, inp_passwd):
    ''' This function is used to authenticate with satellite server
    and return the key to make the other api calls. It also returns
    the list of all systems present in satellite.
    '''
    try:
        # authenticate with satellite
        key = client.auth.login(inp_login, inp_passwd)
    except xmlrpclib.Fault, e:
        print 'xmlrpclib.Fault:', e
        sys.exit(1)
    return key

def system_group(client, key):
    group_list = []
    grp_list = client.systemgroup.listAllGroups(key)
    for sys_grp in grp_list:
        group_list.append(sys_grp['name'])
    while True:
        grp_name = raw_input('Please enter Group name or leave it blank and \
hit enter to list all Groups: ')
        if not grp_name:
            print group_list
        elif grp_name not in group_list:
            print 'System Group does not exist. Please enter again.'
        else:
            break
    return grp_name

def system_list(client, key, grp_name, inp_login):
    systm_list = []
    sys_list = client.systemgroup.listSystems(key, grp_name)
    for system in sys_list:
        sysname = system['profile_name'].replace(' ', '')
        sysname = sysname.replace('.internal.salesforce.com','')
        sysname = sysname.replace('.adstage.salesforce.com','')
        sysid = system['id']
        ocurenc = xmlrpclib.DateTime((datetime.datetime.now()).utctimetuple())
        pre_patch_run = client.system.scheduleScriptRun(key, sysid, \
                'root', 'root', 600, pre_patch_script, ocurenc)
        tag_name = '{0}-{1}-{2}'.format(grp_name, \
                datetime.datetime.now().strftime('%Y%m%d%H%M%S'), inp_login)
        tag_snapshot = client.system.tagLatestSnapshot(key, sysid, tag_name)
        system = {'name': sysname, 'id': sysid, 'pre_patch_run': \
                  pre_patch_run, 'tag_snapshot': tag_snapshot}
        systm_list.append(system)
    return systm_list

if __name__ == '__main__':
    client = satellite_server()
    inp_login, inp_passwd = satellite_creds()
    key = satellite_auth(client, inp_login, inp_passwd)
    grp_name = system_group(client, key)
    systm_list = system_list(client, key, grp_name, inp_login)
    print systm_list
#
#EOF