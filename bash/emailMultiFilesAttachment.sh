#!/usr/bin/env bash
#
# Author: Sumit Goel
#
# Note: Please add all the filenames with full path
# as an arguments to this script. This script is
# tested on Red Hat systems.
#
which uuencode > /dev/null
if [ $? -ne 0 ] ; then
	echo "uuencode: binary file encoder is not present"
	while true; do
		read -p "Do you wish to install \"sharutils\"? [Y/N] " yn
		case $yn in
			[Yy]* ) yum -y -q install sharutils || exit; break;;
			[Nn]* ) exit;;
			* ) echo "Please answer yes or no.";;
		esac
	done
fi

ranVar=$RANDOM
touch /tmp/$ranVar

for argv in $* ; do
	uuencode $argv $(basename $argv) >> /tmp/$ranVar
done

read -p "Enter your email address: " email
read -p "Enter the subject of the email: " msgsub
read -p "Enter the email body: " msgbdy
echo $msgbdy >> /tmp/$ranVar

which mail > /dev/null
if [ $? -ne 0 ] ; then
	echo "mail: command not found"
	while true; do
		read -p "Do you wish to install \"mailx\"? [Y/N] " yn
		case $yn in
			[Yy]* ) yum -y -q install mailx || exit; break;;
			[Nn]* ) exit;;
			* ) echo "Please answer yes or no.";;
		esac
	done
fi
mail -s $msgsub $email < /tmp/$ranVar
echo "Email sent, please check your mail logs for the email status."
rm -rf /tmp/$ranVar
#END
