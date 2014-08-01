#!/bin/bash
# Shell script to monitor the disk space
# Author . Sumit Goel (IT-NOC)
# It will send out an email to IT-NOC, if the percentage
# of disk space is >= 85% or 90% Full of any partition.

ipaddress=`/sbin/ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`;
mailonce=`date +%H`;
 if [ $mailonce -eq 9 ]; then
 /usr/bin/printf "%b" "***** Disk Space Report *****\n\nHost: $(hostname)\nAddress: $ipaddress\nDate/Time: $(date)\n\n $(df -h)" | mail -s "Disk Space Report: $(hostname)" it-noc@salesforce.com
 fi
df -Ph | grep -vE '^Filesystem' | awk '{ print $5 " " $1 " " $6 " " $2 " " $3 }' | while read output;
do
 usepercent=$(echo $output | awk '{ print $1}' | cut -d'%' -f1 )
 partition=$(echo $output | awk '{ print $2 }' )
 mountedon=$(echo $output | awk '{ print $3 }' )
 totalsize=$(echo $output | awk '{ print $4 }' )
 usedspace=$(echo $output | awk '{ print $5 }' )
 if [[ $usepercent != [0-9]* ]]; then
 break
 elif [ $usepercent -ge 90 ]; then
 /usr/bin/printf "%b" "***** Disk Space Alert *****\n\nHost: $(hostname)\nAddress: $ipaddress\nState: Critical\nDate/Time: $(date)\n\nPartition: $partition\nMount Point: $mountedon\nStatus: $usepercent% FULL ($usedspace of $totalsize is Used)\n\nEscalation Contact: Pallav Saikia" | mail -s "Critical: $(hostname): Partition \"$partition\" Mounted on \"$mountedon\" is $usepercent% FULL" it-noc@salesforce.com
 elif [[ $usepercent -gt 85 && $usepercent -lt 90 ]]; then
 /usr/bin/printf "%b" "***** Disk Space Alert *****\n\nHost: $(hostname)\nAddress: $ipaddress\nState: Warning\nDate/Time: $(date)\n\nPartition: $partition\nMount Point: $mountedon\nStatus: $usepercent% FULL ($usedspace of $totalsize is Used)\n\nEscalation Contact: Pallav Saikia" | mail -s "Warning: $(hostname): Partition \"$partition\" Mounted on \"$mountedon\" is $usepercent% FULL" it-noc@salesforce.com
 fi
done