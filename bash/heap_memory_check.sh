#!/bin/bash
# Shell script to monitor the java heap memory utilization
#
# Author: Sumit Goel (sumit.goel@salesforce.com)
#
# It will send out an email to IT-NOC and ITInfraOpsLinuxUnix,
# if the percentage of utilization is >=90% of 2Gb.
#

# Java process ID
JAVAPID=`/sbin/pidof java | awk '{print $1}'`

# Heap summary
HEAPSTATUS=`/home/intranet/tools/jdk/jdk1.6.0_01/bin/jmap -heap $JAVAPID`

# Sum of in use Heap
HEAPINUSE=`echo "$HEAPSTATUS" | grep used | grep -v '%' | cut -d= -f2 | awk '{s+=$1} END {print s}'`

# Calculate the percentage
INUSEPERCENT=`echo "scale=0; $HEAPINUSE*100/2147483648" | bc`

# If >=90% send email alert to NOC and Linux team
if [ $INUSEPERCENT -ge 95 ]; then
printf "***** Heap Memory Utilization Alert *****\n\nHost: $(hostname -s)\nDate/Time: $(date)\nCurrent Utilization: $INUSEPERCENT%%\n\nIT-NOC, Please prepare yourself for end user communication and Intranet restart as per the SOP.\n $HEAPSTATUS" | mail -s "Alert: $(hostname -s): Heap Memory Utilization is $INUSEPERCENT%" it-noc@salesforce.com ITInfraOpsLinuxUnix@salesforce.com
fi

# Send Heap summary to file
printf "===== $(date +%F..%T..%Z) ===== Utilization $INUSEPERCENT%% =====\n $HEAPSTATUS\n\n" >> /home/intranet/dumps/heap_memory_utilization

#EOF