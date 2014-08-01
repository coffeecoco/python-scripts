#!/bin/bash
# Script: p4_client_upgrade.sh
# Description:
#	1. Script will check for existing P4 client binary at $P4_PATH
#	2. If found then it will rename the existing P4 client binary
#		and upload new binary
#	3. If not then it will upload the new P4 client binary. 
# Author: Sumit Goel (hello@sumitgoel.me)
# Revision 1.0: January 14, 2013
#

#Safely obtain short hostname
SHORT_HOSTNAME=`uname -n | awk -F"." ' { print $1 } '`

P4_PATH="/usr/local/bin/p4"

p4upgrade(){
	umount /mnt
	mkdir -p /mnt/p4
	mount -t nfs nas-dist:/vol/vol5/dist/P4_Client /mnt/p4
	cp /mnt/p4/p4 $P4_PATH
	chmod +x $P4_PATH
	umount /mnt/p4
}

if [ -f "$P4_PATH" ]
then
	cp -ap $P4_PATH $P4_PATH.`date +%F`
	rm -rf $P4_PATH
	p4upgrade
else
	p4upgrade
fi

#
#EOF