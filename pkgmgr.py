#!/usr/bin/env python -tt

# Author: Sumit Goel
# Description: A program to automate the process of adding and removing
#    interdependent software packages.

import sys
try:
    import getpass
except ImportError, e:
    print e
    sys.exit(1)

# list of all installed packages
installed_packages = []

def user_input():
    """ Capture the user commands and return a two dimensional array for
    sequential processing and an array for DEPEND commands to lookup
    INSTALL and REMOVE command dependencies later.
    """
    commands = ['INSTALL', 'REMOVE', 'LIST']
    # list of all user input commands
    all_input = []
    # list of all user input DEPEND command
    dep_input = []
    user_input = None
    non_repeat_input = 'DEPEND'
    # loop to user input
    for user_input in iter(raw_input, 'END'):
        # split the command into a list
        user_input = user_input.split()
        # if user input is blank
        if not user_input:
            continue
        # else if it is the first entry and user command == non_repeat_input
        elif not all_input and user_input[0] == non_repeat_input:
            all_input.append(user_input)
            dep_input.append(user_input)
        # else if all entries so far are == non_repeat_input 
        # and current command == non_repeat_input
        elif user_input[0] == non_repeat_input and all(command[0] == \
                non_repeat_input for command in all_input):
            all_input.append(user_input)
            dep_input.append(user_input)
        # else if it is one of the valid commands
        elif all_input and user_input[0] in commands:
            all_input.append(user_input)
        # else user input is not a valid command
        else:
            print '>>> INVALID COMMAND'
    return (all_input, dep_input)


def install_package(package, dep_input):
    """ Installs the package and it's dependencies as per the user input
    sequencially.
    """
    iteration = 0
    notexist = 0
    # iterate over all dependency command lines
    for row in dep_input:
        if iteration == 1:
            break
        else:
            for field in row:
                # if any dependency matches the install command package
                if field == package:
                    iteration = 1
                    # find the position of the package and create a range
                    # with the length of list and iterate over the reversed
                    # range
                    for i in reversed(range(row.index(field), len(row))):
                        # if the package is already installed
                        if row[i] in installed_packages:
                            print '\t%s is already installed' % row[i]
                        # else install the package
                        else:
                            print '\t%s successfully installed' % row[i]
                            installed_packages.append(row[i])
                else:
                    notexist = 1
    # if the package is not present in any dependencies command
    if notexist == 1 and package not in installed_packages:
        print '\t%s successfully installed' % package
        installed_packages.append(package)


def remove_package(package, dep_input):
    """ Removes the package if it is not alreay used by some other package
    in dependency commands
    """
    pkg_instd = 0
    package_position = []
    chk_aft_remv = []
    # if package is not installed
    if package not in installed_packages:
        print '\t%s is not installed' % package
    # else if package in installed packages list
    elif package in installed_packages:
        for row in dep_input:
            for field in row:
                if field == package:
                    # index the row number and package 
                    package_position.append([dep_input.index(row), \
                            row.index(field)])
        # dictionary of all the values in each row of DEPEND command
        field_idices = dict((field, i) for row in dep_input for i, field \
                in enumerate(row))
        idx = field_idices.get(package)
        # if package is installed and not in installed packages list
        if idx is None:
            installed_packages.remove(package)
            print '\t%s successfully removed' % package
        # iterate over the package and dependency index list
        for row in package_position:
            if len(package_position) == 1:
                # if only one matching row and field not dependent
                if row[1] == 1:
                    installed_packages.remove(dep_input[row[0]][row[1]])
                    print '\t%s successfully removed' % package
                    # repeat the process for the package needed 
                    # by this package
                    if len(dep_input[row[0]]) - 1 >= row[1] + 1:
                        chk_aft_remv.append(dep_input[row[0]][row[1] + 1])
                # else if the dependent package in the installed list
                elif dep_input[row[0]][row[1] - 1] in installed_packages:
                    print '\t%s is still needed' % package
                # else if the dependent package is not in installed list
                elif dep_input[row[0]][row[1] - 1] not in \
                        installed_packages:
                    installed_packages.remove(dep_input[row[0]][row[1]])
                    print '\t%s successfully removed' % package
                    # append the package needed by this package
                    if len(dep_input[row[0]]) - 1 >= row[1] + 1:
                        chk_aft_remv.append(dep_input[row[0]][row[1] + 1])
            # else if more than one matching row and dependent package
            # in installed list
            elif row[1] != 1 and dep_input[row[0]][row[1] - 1] in \
                    installed_packages:
                print '\t%s is still needed' % package
                break
            # else if more than one matching row and dependent package
            # not in installed list
            elif row[1] != 1 and dep_input[row[0]][row[1] - 1] not in \
                    installed_packages:
                # if this is the last row of iteration
                if package_position.index(row) == len(package_position) \
                        - 1 and pkg_instd == 1:
                    installed_packages.remove(dep_input[row[0]][row[1]])
                    print '\t%s successfully removed' % package
                    # append the package needed by this package
                    if len(dep_input[row[0]]) - 1 >= row[1] + 1:
                        chk_aft_remv.append(dep_input[row[0]][row[1] + 1])
                pkg_instd = 1
                continue
            # else if found in multiple lines at first position
            elif row[1] == 1 and package == dep_input[row[0]][row[1]]:
                # if this is the last row of iteration
                if package_position.index(row) == len(package_position) \
                        - 1 and pkg_instd == 1:
                    installed_packages.remove(dep_input[row[0]][row[1]])
                    print '\t%s successfully removed' % package
                    # append the package needed by this package
                    if len(dep_input[row[0]]) - 1 >= row[1] + 1:
                        chk_aft_remv.append(dep_input[row[0]][row[1] + 1])
                pkg_instd = 1
                continue
            # elif first item in a row but not equal to package
            elif row[1] == 1 and package != dep_input[row[0]][row[1]]:
                continue
    # iterate over the needed packages
    for item in chk_aft_remv:
        remove_package(item, dep_input)


def input_processing(all_input, dep_input):
    """ Process the user commands sequentially as the input order may
    have some dependecies.
    """
    all_input.append(['END'])
    for row in all_input:
        # print the user input DEPEND command
        if row[0] == 'DEPEND':
            print ' '.join(row)
        # process the package installation
        if row[0] == 'INSTALL':
            print ' '.join(row)
            install_package(row[1], dep_input)
        # process the package removal
        if row[0] == 'REMOVE':
            print ' '.join(row)
            remove_package(row[1], dep_input)
        # print the list of currently installed packages
        if row[0] == 'LIST':
            print ' '.join(row)
            for pkg in installed_packages:
                print '\t%s' % pkg
        # print the input submission END command
        if row[0] == 'END':
            print ' '.join(row)
        else:
            continue


# program output header
print '''=====================================================
Hi %s,

Some assumptions were made while writing the program,
 1. The requirements did not clarify where the packages are located and in 
    what format like rpm or any other binary package format, yum repository,
    source code and etc. So, the assumption was made to focus on program
    logic not on the actual installation or removal of packages as that
    part is fairly easy after the proper logic. The program can be easily
    tweaked to update the steps.
 2. INSTALL and REMOVE commands will take one package in a line.
 3. There will be at least one DEPEND command before any INSTALL, REMOVE
    and LIST commands.
 4. DEPEND command will not have any conflicting and incomplete package
    dependencies. For example,
        DEPEND item1 item2 item3
        DEPEND item5 item3 item4
        INSTALL item2
        INSTALL item3
        END
    In this example, either first DEPEND command is incomplete or second
    DEPEND command is conflicting with first.
 5. Last but not the least, Python and required modules are installed on
    the system.

As per the requirements only below 5 commands are allowed,

DEPEND   defines package dependency
INSTALL  installs package and it's dependencies
REMOVE   removes package if not used by any other package
LIST     lists the names of all currently installed packages
END      marks the end of input, when used in a line by itself

Please enter your input now:
=====================================================''' % getpass.getuser()

# execute function to capture user commands
try:
    all_input, dep_input = user_input()
except:
    print ''
    sys.exit(1)

# user confirmation to submit the commands for processing
user_inp = raw_input('Do you want to submit the input now? [Y/N]: ')
if user_inp in ('Y', 'y', 'Yes', 'YES'):
    try:
        input_processing(all_input, dep_input)
    except:
        print ''
        sys.exit(1)
# exit the program if user does not confirm
else:
    print 'Please start over, good bye!'
    sys.exit(1)

#
#EOF
