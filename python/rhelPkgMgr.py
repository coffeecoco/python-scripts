#!/usr/bin/env python

# Author: Sumit Goel <sumit.goel@salesforce.com>
# Description: 
#

def HEADER():
  """ Following assumtions were made while writing this script:
  1. The script will be used on RHEL 5 and 6 systems
  2. Python and required list of modules are installed on the system
  3. The commands INSTALL and REMOVE will have only one argument in a line
  4. Yum is configured on the system to install/remove the packages although
     the script does not use yum operating system command instead it uses Yum 
     Python binding to install and remove packages
  5. User will provide all the DEPEND commands before INSTALL, REMOVE, LIST or END
     and finally will use END command to submit the INPUT for processing
  """

def INPUT():
  ALL_COMMANDS = ['DEPEND','INSTALL', 'REMOVE', 'LIST', 'END']
  USER_INPUT = []
  INPUT_DEPEND = []
  for ROW in iter(raw_input, ALL_COMMANDS[4]):
    ROW = ROW.split()
    if len(USER_INPUT) == 0:
      if ROW[0] == ALL_COMMANDS[0]:
        USER_INPUT.append(ROW)
	INPUT_DEPEND.append(ROW)
      else:
        print '>>> Invalid Input'
    elif ROW[0] == ALL_COMMANDS[0]:
      USER_INPUT.append(ROW)
      INPUT_DEPEND.append(ROW)
    elif ROW[0] not in ALL_COMMANDS:
      print '>>> Invalid Input'
    else:
      try:
        ALL_COMMANDS.remove('DEPEND')
      except ValueError, e:
        pass
      USER_INPUT.append(ROW)
  return (USER_INPUT, INPUT_DEPEND)

def INPUT_PROCESSING(USER_INPUT, INPUT_DEPEND):
  USER_INPUT.append(['END'])
  for ROW in USER_INPUT:
    if ROW[0] == 'DEPEND':
      print ' '.join(ROW)
    elif ROW[0] == 'INSTALL':
      print ' '.join(ROW)
    elif ROW[0] == 'REMOVE':
      print ' '.join(ROW)
    elif ROW[0] == 'LIST':
      print ' '.join(ROW)
    elif ROW[0] == 'END':
      print ' '.join(ROW)
    else:
      continue

USER_INPUT, INPUT_DEPEND = INPUT()
INPUT_PROCESSING(USER_INPUT, INPUT_DEPEND)

__author__ = 'Sumit Goel'
__email__  = 'sumit.goel@salesforce.com'

#EOF
