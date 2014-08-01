#!/usr/bin/env bash
#
# Author: Sumit Goel
# Email: sumit.goel@outlook.com
# Description: 
#

CONFIGURESNMPV3(){
	# Most probably Net-SNMP should already be installed
	# but just in case if not installed then it will install that
	yum -y -q install net-snmp net-snmp-devel net-snmp-utils
	/etc/init.d/snmpd stop
	mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.`date +%F-%H%M%S`
	# Fetching the function argument
	mv $1 $1.`date +%F-%H%M%S`
	# Replace 1234567890 with the two different strong passwords
	/usr/bin/net-snmp-config --create-snmpv3-user -ro -A MD5 -a 1234567890 -X AES -x 1234567890 snmpv3rouser
	chkconfig snmpd on
	/etc/init.d/snmpd start
}

# The file location to store the encrypted passwords is different
# in RHEL5 and RHEL6 systems
KERNELVERSION=`uname -r`
if echo $KERNELVERSION | grep -q -i el5; then
	CONFIGURESNMPV3 /var/net-snmp/snmpd.conf
elif echo $KERNELVERSION | grep -q -i el6; then
	CONFIGURESNMPV3 /var/lib/net-snmp/snmpd.conf
else
	echo "Please check the system, doesn't seem to be RHEL 5 or 6."
	exit 1
fi

# If this is a dell physical machine and OMSA is installed
# then it will proxy the hardware event to Net-SNMP
which srvadmin-services.sh
if [ $? -ne 0 ] ; then
	/etc/init.d/dataeng enablesnmp
	/opt/dell/srvadmin/sbin/srvadmin-services.sh restart
	/bin/echo "smuxpeer .1.3.6.1.4.1.674.10892.1" >> /etc/snmp/snmpd.conf
	/bin/echo "smuxpeer .1.3.6.1.4.1.674.10893.1" >> /etc/snmp/snmpd.conf
	/etc/init.d/snmpd restart
fi
