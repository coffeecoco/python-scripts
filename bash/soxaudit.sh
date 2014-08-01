#!/usr/bin/env bash
#
# Author: Sumit Goel
# Description: The script will execute another script and email the output.
#

## Check if uuencode command is present, if not then install the required package on RHEL system
which uuencode > /dev/null

if [ $? -ne 0 ] ; then
  yum -y -q install sharutils
  if [ $? -ne 0 ] ; then
    echo "Problem installing sharutils package, command uuencode won't work. Exiting.."
    exit 1
  fi
fi
## END

## Flush the Centrify Agent cached data
/usr/sbin/adflush -f

## Update the Active Directory Group Policies for Centrfy Agent
/usr/bin/adgpupdate

## Mount the NAS Share and capture the command output
DIRECTORY=$RANDOM
FILENAME="$(hostname -s)-$DIRECTORY-$(date +%F).rtf"
MOUNTPATH="/tmp/$DIRECTORY"

/bin/mkdir $MOUNTPATH
/bin/mount nas-dist:/vol/vol5/dist $MOUNTPATH

/usr/bin/adinfo > /tmp/$FILENAME
echo "" >> /tmp/$FILENAME
echo "##############################" >> /tmp/$FILENAME
echo "" >> /tmp/$FILENAME
$MOUNTPATH/scripts/list_users.pl >> /tmp/$FILENAME
## END

## Attach the captured data to Supportforce case using Email2Case address
SUPPORTFORCE_CASE_REF_NUM="ref:_00D00hg76._50070eR4ob:ref"
EMAIL_SUBJECT="$(hostname -s) Server Admins $SUPPORTFORCE_CASE_REF_NUM"
EMAIL_TO="io-linux-e2c@salesforce.com"

/usr/bin/uuencode /tmp/$FILENAME /tmp/$FILENAME | /bin/mail -s "$EMAIL_SUBJECT" $EMAIL_TO

if [ $? -ne 0 ] ; then
  echo "Problem encoding or sending an email from the server."
  exit 1
fi
## END

## Unmount the NAS share
/bin/umount $MOUNTPATH

## Delete the file
rm -f /tmp/$FILENAME

#
#EOF
