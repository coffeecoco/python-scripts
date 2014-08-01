#!/bin/bash
# Script: solaris_disk_inode_check.sh
# Description:
#	1. Script will monitor the disk inode usage on Sun Solaris server.
#	2. Script will send an email notification alert if inode usage goes over 90%.
#	3. Script will record the data in CSV format for trend analysis.
# Author: Sumit Goel (hello@sumitgoel.me)
# Revision 1.0: January 10, 2013
#

#Safely obtain short hostname
SHORT_HOSTNAME=`uname -n | awk -F"." ' { print $1 } '`

#Exclude list of unwanted partitions, if several partitions then use "|" to separate the partitions
EXCLUDE_LIST=""

df -F ufs -o i | egrep -v -e '^Filesystem|${EXCLUDE_LIST}' | awk '{ print $4 " " $1 " " $5 " " $2 " " $3 }' | while read OUTPUT;

do
INODEUSEPERCENT=`echo $OUTPUT | awk '{ print $1}' | cut -d'%' -f1` 
PARTITION=`echo $OUTPUT | awk '{ print $2 }'` 
MOUNTEDON=`echo $OUTPUT | awk '{ print $3 }'`
INODEUSED=`echo $OUTPUT | awk '{ print $4 }'`
INODEFREE=`echo $OUTPUT | awk '{ print $5 }'`

#INODE usage data (for trend analysis) file location and name
INODE_USAGE_DATA="/tmp/inode_usage_data.csv"

FILE_HEADER="Timestamp,Filesystem,iused,ifree,%iused,Mounted on"

if [ -f "$INODE_USAGE_DATA" ]
then
	echo "`date`,$PARTITION,$INODEUSED,$INODEFREE,$INODEUSEPERCENT%,$MOUNTEDON" >> $INODE_USAGE_DATA
else
	touch $INODE_USAGE_DATA
	echo "$FILE_HEADER" > $INODE_USAGE_DATA
	echo "`date`,$PARTITION,$INODEUSED,$INODEFREE,$INODEUSEPERCENT%,$MOUNTEDON" >> $INODE_USAGE_DATA
fi

#Email list to receive notification, if several addresses then use space to separate the partitions
EMAIL_TO="hello@sumitgoel.me"

EMAIL_SUBJECT="Alert: $SHORT_HOSTNAME - $MOUNTEDON Almost out of INODE numbers $INODEUSEPERCENT% Used"

EMAIL_BODY_LINE1="***** Disk INODE Alert *****"
EMAIL_BODY_LINE2="Host: $SHORT_HOSTNAME"
EMAIL_BODY_LINE3="Partition: $PARTITION"
EMAIL_BODY_LINE4="Mounted On: $MOUNTEDON"
EMAIL_BODY_LINE5="Status: $INODEUSEPERCENT% Used"
EMAIL_BODY_LINE6="Escalation: On-Call Systems Engineer"
EMAIL_BODY_LINE7="System inode Status: df -F ufs -o i"
EMAIL_BODY_LINE8=`df -F ufs -o i`

if [ $INODEUSEPERCENT -ge 90 ]; then
echo "$EMAIL_BODY_LINE1\n\n$EMAIL_BODY_LINE2\n$EMAIL_BODY_LINE3\n$EMAIL_BODY_LINE4\n$EMAIL_BODY_LINE5\n$EMAIL_BODY_LINE6\n\n$EMAIL_BODY_LINE7\n\n$EMAIL_BODY_LINE8" | mailx -s "$EMAIL_SUBJECT" $EMAIL_TO
fi
done

#
#EOF