#!/usr/bin/env bash

# Author: Sumit Goel
# Description: Change the default SNMPD logging level to avoid the
#     informational messages.

# Check if lsb_release command is present if not then install
# the redhat-lsb package and if not able to install package
# then exit out of the script
which lsb_release > /dev/null
if [ $? -ne 0 ] ; then
  yum -y -q install redhat-lsb
  if [ $? -ne 0 ] ; then
    echo "Problem installing redhat-lsb package. Exiting.."
    exit 1
  fi
fi

# Check the RHEL major version and based on that backup the config file,
# empty the config file and add the right config and restart the snmpd
# daemon
rhelversion=$(lsb_release -rs | cut -f1 -d.)
# if RHEL5
if [ "$rhelversion" -eq "5" ]; then
    cp -ap /etc/sysconfig/snmpd.options /etc/sysconfig/snmpd.options.`date +%F`
    cp /dev/null /etc/sysconfig/snmpd.options
    printf "OPTIONS=\"-LS0-5d -Lf /dev/null -p /var/run/snmpd.pid\"\n" \
        >> /etc/sysconfig/snmpd.options
    /etc/init.d/snmpd restart
# if RHEL6
elif [ "$rhelversion" -eq "6" ]; then
    cp -ap /etc/sysconfig/snmpd /etc/sysconfig/snmpd.`date +%F`
    cp /dev/null /etc/sysconfig/snmpd.options
    printf "OPTIONS=\"-LS0-5d -Lf /dev/null -p /var/run/snmpd.pid\"\n" \
        >> /etc/sysconfig/snmpd
    /etc/init.d/snmpd restart
# if couldn't find RHEL5 or RHEL6
else
    exit 1
fi
