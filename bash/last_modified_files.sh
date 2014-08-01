#!/bin/bash
#####################################################################################
# Script: email_modified_files.sh                                    
# Description: Send an email if any file is modified or created in last 10 minutes.
#
# Header: /opt/scripts/
# Date: 11/30/2012
# Author: Sumit Goel (hello@sumitgoel.me)
#####################################################################################
SHORT_HOSTNAME=`hostname -s`
LOCATION="/home"
#
DESTINATION="$1"
if [ -z "$1" ]
then
  DESTINATION="$LOCATION"
fi
#
EMAIL_TO="hello@sumitgoel.me"
EMAIL_SUBJECT="List Last Modified files from $SHORT_HOSTNAME"
EMAIL_BODY_Line1="Below is the list of last modified files:"
#
MOD_FILES=`find $DESTINATION -type f -mmin -10 -ls`
#
if [ -n "$MOD_FILES" ]
then
  printf "$EMAIL_BODY_Line1\n\n$MOD_FILES\n" | mail -s "$EMAIL_SUBJECT" $EMAIL_TO
fi
#
#EOF