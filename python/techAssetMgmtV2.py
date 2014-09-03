#!/usr/bin/env python

# Author: Sumit Goel
# Description: A program to compare the Tech Assets data in CSV file with
#     the Red Hat Satellite server. The program will create for the CSV
#     for processing and create two CSV files with the differences in
#     Tech Assets and Red Hat Satellite server.

import sys
try:
  import socket
  import xmlrpclib
  import getpass
  import time
  import csv
  import re
  import textwrap
except ImportError, e:
  print 'ImportError:', e
  sys.exit(1)

# directory path to create CSV files
csvpath = '/Users/sumit.goel/Downloads/'

# output csv file name and file path
file_name = csvpath + 'formatted_' + time.strftime('%Y%m%d%H%M%S') + \
        '.csv'

# header for data loader CSV file
csv_header = ['RECORDTYPEID', 'STATE__C', 'HOST_NAME__C', \
        'OPERATING_SYSTEM__C', 'STAGE__C', 'CPU__C', 'RAM__C', \
        'IP_ADDRESS_1__C', 'SERIAL_NUMBER__C', 'SERVICE__C', \
        'CONTACT_NAME__C', 'OWNING_DEPARTMENT_CODE__C', 'NAME']

def no_argument():
    ''' This function will check for command line arguments and if no
    argument is given then exit the program with a message.
    '''
    if len(sys.argv) == 1:
        print sys.argv[0] + ': missing argument'
        print 'Please pass the CSV file as an argument.',
        sys.exit(1)
    return

def format_csv():
    ''' This function will remove any blank rows and footer in the
    downloaded CSV file from the report.
    '''
    # open the CSV file in read mode
    with open(sys.argv[1], 'rU') as csv_open:
        csv_reader = csv.reader(csv_open, delimiter=',')
        print '... reading the CSV file ...'
        # open a new CSV file in write mode
        with open(file_name, 'wb') as file_open:
            file_writer = csv.writer(file_open, delimiter=',', \
                    quoting=csv.QUOTE_ALL)
            # write the header row from csv reader
            file_writer.writerow(next(csv_reader))
            print '... formatting the data in the CSV file ...'
            # read a row at time from csv reader
            for row in csv_reader:
            # if more than 3 columns in csv
                if len(row) > 2:
                    file_writer.writerow(row)
    print '... new CSV file created with formatted data ...'
    print '... %s ...' % file_name

def duplicate_hostname():
    ''' This function will read the formatted tech assets CSV file and will
    create a new CSV file with the duplicate host names and exit out of
    the program to address any duplicate host names.
    '''
    dup_found = None
    dup_csv = csvpath + 'duplicate_hostname_' + \
            time.strftime('%Y%m%d%H%M%S') + '.csv'
    # open the formatted tech assets csv
    with open(file_name, 'rb') as file_open:
        file_reader = csv.reader(file_open, delimiter=',')
        print '... reading the formatted CSV file ...'
        # open new csv file to write duplicate hostnames
        with open(dup_csv, 'wb') as dup_open:
            dup_writer = csv.writer(dup_open, delimiter=',', \
                    quoting=csv.QUOTE_ALL)
            # write the header row
            dup_writer.writerow(next(file_reader))
            print '... checking for any duplicate host names ...'
            # blank set of host names
            uniq_host_names = set()
            # read each row and if host name not present in the set
            # then add the hostname else write the duplicate entry
            # in the file
            for row in file_reader:
                if row[2] not in uniq_host_names:
                    uniq_host_names.add(row[2])
                else:
                    dup_found = 1
                    dup_writer.writerow(row)
            # if duplicate host name found then 
            if dup_found == 1:
                message = '''
                ... duplicate host names found ...
                ... please address the dulicate host names in ...
                ... file: %s ...
                ... and run the program again ...
                ''' % dup_csv
                # don't indent the message text
                dedented_message = textwrap.dedent(message).strip()
                print dedented_message
                sys.exit(1)
            else:
                print '... no duplicates found ...'

def index_hostnames():
    ''' This function is used to create a dictionary of host names from
    tech assets CSV file.
    '''
    # open the formatted tech assets CSV file
    with open(file_name, 'rb') as file_open:
        file_reader = csv.reader(file_open, delimiter=',')
        # create a dictionary
        host_indices = dict((r[2], i) for i, r in enumerate(file_reader))
    return host_indices

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
    ''' This function is used to authenticae with satellite server
    and return the key to make the other api calls. It also returns
    the list of all systems present in satellite.
    '''
    try:
        # authenticate with satellite
        key = client.auth.login(inp_login, inp_passwd)
        # api call to pull the list of all systems
        allsystems = client.system.listSystems(key)
    except xmlrpclib.Fault, e:
        print 'xmlrpclib.Fault:', e
        sys.exit(1)
    return (key, allsystems)

def system_dmi(client, key, sysid):
    ''' This function uses satellite API to fetch the system DMI (Desktop
    Management Interface) information. It calculates the system serial
    number in the DMI information and return if it is virtual or physical
    system.
    '''
    # api call to pull the DMI information
    systemdmi = client.system.getDmi(key, sysid)
    # caluclates the serial number from asset key of the system DMI
    sysasset = systemdmi['asset'].replace(' ', '')
    sysasset = sysasset.replace('.', '')
    serialno = re.search(r'(system):([\w-]+)', sysasset)
    # if system serail number found
    if serialno:
        serialno = serialno.group(2)
        if serialno.startswith('VMware-'):
            serialno = serialno.replace('VMware-', '')
            serialno = serialno.replace('-', '')
            # format the serial number in VMware UUID form
            serialno = '%s{dash}%s{dash}%s{dash}%s{dash}%s'.format( \
                    dash='-') % (serialno[:8], serialno[8:12], \
                    serialno[12:16], serialno[16:20], serialno[20:])
            # record type ID for virtual systems
            recordtype = '01270000000Dvhd'
        else:
            # record type ID for physical systems
            recordtype = '01270000000Dvhc'
    # if system serial number not found than assume it's a open compute
    # physical system and set the serial number to none
    else:
        # record type ID for physical systems
        recordtype = '01270000000Dvhc'
        serialno = None
    return (serialno, recordtype)

def system_cpu(client, key, sysid):
    ''' This function uses satellite API to fetch the CPU information
    assigned to the system.
    '''
    # api call to pull the CPU information
    syscpu = client.system.getCpu(key, sysid)
    # number of CPUs assigned to the system
    if syscpu['count']:
        syscpucount = syscpu['count']
    # if CPU is 32bit or 64bit
    if syscpu['arch']:
        if syscpu['arch'] == 'x86_64':
            arch = 'x86_64'
        else:
            arch = 'x86'
    return (syscpucount, arch)

def system_kernel(client, key, sysid, arch):
    ''' This function uses satellite API to fetch the running
    kernel on the system and return the operating system using
    CPU arch and running kernel version.
    '''
    # api call to pull the running kernel version
    syskernel = client.system.getRunningKernel(key, sysid)
    if syskernel:
        kernel_ver = syskernel
        # if kernel version starts with 2.6.9 then it's a RHEL4
        if kernel_ver.startswith('2.6.9'):
            sysos = 'RHEL4 (%s)' % arch
        # if kernel version starts with 2.6.18 then it's a RHEL5
        elif kernel_ver.startswith('2.6.18'):
            sysos = 'RHEL5 (%s)' % arch
        # if kernel version starts with 2.6.32 then it's a RHEL6
        elif kernel_ver.startswith('2.6.32'):
            sysos = 'RHEL6 (%s)' % arch
    return (kernel_ver, sysos)

def system_network(client, key, sysid):
    ''' This function uses satellite API to fetch the active IP
    address on the system.
    '''
    # api call to pull the network information
    sysnet = client.system.getNetwork(key, sysid)
    if sysnet['ip']:
        sysnetip = sysnet['ip']
    return sysnetip

def system_memory(client, key, sysid):
    ''' This function uses satellite API to fetch the RAM and Swap
    assigned to the system.
    '''
    # api call to pull the memory information
    sysmem = client.system.getMemory(key, sysid)
    if sysmem['ram']:
        sysram = sysmem['ram']
    if sysmem['swap']:
        sysswap = sysmem['swap']
    return (sysram, sysswap)

def system_info(client, key, allsystems, host_indices):
    ''' This function will search the systems in tech assets CSV
    and if system not found then create a new CSV file with the
    information to insert using data loader.
    '''
    # empty dictionary for satellite system name and id
    satsysdict = {}
    # new CSV file name
    insert_csv = csvpath + 'dl_insert_' + time.strftime('%Y%m%d%H%M%S') \
            + '.csv'
    # open the new CSV file in write mode
    with open(insert_csv, 'wb') as insert_open:
        insert_writer = csv.writer(insert_open, delimiter=',', \
                quoting=csv.QUOTE_ALL)
        # write the header row in the new CSV
        insert_writer.writerow(csv_header)
        for system in allsystems:
            # satellite system id
            sysid = system['id']
            # satellite system name
            sysname = system['name'].replace(' ', '')
            sysname = sysname.replace('.internal.salesforce.com','')
            sysname = sysname.replace('.adstage.salesforce.com','')
            # update satellite system name and id dictionary
            satsysdict[sysname] = sysid
            # search for satellite system name in the dictionary of host
            # names from tech assets CSV file
            index = host_indices.get(sysname)
            # if system not found then fetch more information about the
            # system from satellite and create an entry in CSV file
            if index is None:
                serialno, recordtype = system_dmi(client, key, sysid)
                syscpucount, arch = system_cpu(client, key, sysid)
                kernel_ver, sysos = system_kernel(client, key, sysid, arch)
                sysnetip = system_network(client, key, sysid)
                assetname = sysname + '-' + serialno
                insert_writer.writerow([recordtype, 'On', sysname, sysos, \
                        '', syscpucount, '', sysnetip, serialno, \
                        'a2H700000004OipEAE', '', \
                        '935 - IT - Infrastructure and Operations', \
                        assetname])
    return satsysdict

def asset_update(client, key, satsysdict):
    '''
    '''
    update_csv_header = csv_header
    update_csv_header.append('Id')
    update_csv = csvpath + 'dl_update_' + time.strftime('%Y%m%d%H%M%S') \
            + '.csv'
    manual_csv = csvpath + 'manual_' + time.strftime('%Y%m%d%H%M%S') \
            + '.csv'
    with open(file_name, 'rb') as file_open:
        file_reader = csv.reader(file_open, delimiter=',')
        with open(update_csv, 'wb') as update_open:
            update_writer = csv.writer(update_open, delimiter=',', \
                    quoting=csv.QUOTE_ALL)
            update_writer.writerow(update_csv_header)
            with open (manual_csv, 'wb') as manual_open:
                manual_writer = csv.writer(manual_open, delimiter=',', \
                        quoting=csv.QUOTE_ALL)
                manual_writer.writerow(next(file_reader))
                for row in file_reader:
                    # set record if physical or virtual
                    if row[0] == 'IT Virtual System':
                        recordtype = '01270000000Dvhd'
                    elif row[0] == 'IT Physical System':
                        recordtype = '01270000000Dvhc'
                    # get the system id if host name exist
                    sysid = satsysdict.get(row[2])
                    if sysid is None:
                        manual_writer.writerow(row)
                    else:
                        syscpucount, arch = system_cpu(client, key, sysid)
                        kernel_ver, sysos = system_kernel(client, key, \
                                sysid, arch)
                        sysnetip = system_network(client, key, sysid)
                        if row[3] not in (None, ''):
                            sysos = row[3]
                        if row[11] in (None, ''):
                            dep = '935 - IT - Infrastructure and Operations'
                        else:
                            dep = row[11]
                        update_writer.writerow([recordtype, row[1], \
                                row[2], sysos, '', syscpucount, '', \
                                sysnetip, row[8], 'a2H700000004OipEAE', \
                                '', dep, row[12], row[13]])


if __name__ == '__main__':
    no_argument(), format_csv(), duplicate_hostname()
    client = satellite_server()
    inp_login, inp_passwd = satellite_creds()
    key, allsystems = satellite_auth(client, inp_login, inp_passwd)
    host_indices = index_hostnames()
    satsysdict = system_info(client, key, allsystems, host_indices)
    asset_update(client, key, satsysdict)
    client.auth.logout(key)

#
#EOF
