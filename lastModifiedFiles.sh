#!/bin/bash
#
# Author: Sumit Goel
# Email: sumit.goel@outlook.com
# Description: http://goo.gl/Rka9Gs
#

SHORT_HOSTNAME=`hostname -s`

# Update the directory path here, /opt is script default
LOCATION="/opt"

DESTINATION="$1"
if [ -z "$1" ]
then
	DESTINATION="$LOCATION"
fi

# Update your notification email address here
EMAIL_TO="email@example.com"

EMAIL_SUBJECT="Last Modified files from $SHORT_HOSTNAME"
EMAIL_BODY_Line1="Here is the list of last modified files from $DESTINATION:"

# Update the lookup time here, by default script will check files modified in last 10 minutes
# Remember this lookup time while setting up cronjob for the script
MOD_FILES=`find $DESTINATION -type f -mmin -10 -ls`

if [ -n "$MOD_FILES" ]
then
	printf "$EMAIL_BODY_Line1\n\n$MOD_FILES\n" | mail -s "$EMAIL_SUBJECT" $EMAIL_TO
fi
#
#EOF
