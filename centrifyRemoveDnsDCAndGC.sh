#!/usr/bin/env bash
#
# Author: Sumit Goel
#
pidof adclient > /dev/null
if [ $? -ne 0 ] ; then
        echo "Centrify DirectControl adclient is not running."
        echo "There will be no changes. Exiting.."
        exit
fi

grep -E "dns.dc|dns.gc" /etc/centrifydc/centrifydc.conf > /dev/null
if [ $? -eq 0 ]; then
        cp -ap /etc/centrifydc/centrifydc.conf /etc/centrifydc/centrifydc.conf.bak-`date +%F-%H%M%S`
        sed -i 's/^dns.dc/# dns.dc/g' /etc/centrifydc/centrifydc.conf
        sed -i 's/^dns.gc/# dns.gc/g' /etc/centrifydc/centrifydc.conf
        /etc/init.d/centrifydc restart
        adflush --force
        adgpupdate
fi
#END
