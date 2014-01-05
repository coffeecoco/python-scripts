#!/usr/bin/env bash
#
# Author: Sumit Goel
# Email: sumit.goel@outlook.com
# Description: 
#

# Update your volume group name
VGNAME="vg_sys"
# Update your logical volume name
LVNAME="lv_opt"
# Update the threshold
THRESHOLD=2560

VGFREESPACE=`vgs -o vg_free --noheadings $VGNAME | tr -d ' ' | cut -d"." -f1`
LVSIZE=`lvs -o lv_size --noheadings /dev/$VGNAME/$LVNAME | tr -d ' ' | cut -d"." -f1`

if [ "$LVSIZE" -lt "$THRESHOLD" ]; then
	INCREASEBY=$(($THRESHOLD - $LVSIZE))
	INCREASEBY=10
	if [ "$VGFREESPACE" -gt "$INCREASEBY" ]; then
		lvextend -L+"$INCREASEBY"M -r /dev/$VGNAME/$LVNAME
	else
		echo "Not enough free space in volume group"
		exit 1
	fi
fi