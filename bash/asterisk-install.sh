#!/bin/bash

LOCATION=/opt

yum -y groupremove --skip 'DNS Name Server'  
yum -y groupremove --skip 'Editors'  
yum -y groupremove --skip 'Legacy Network Server'  
yum -y groupremove --skip 'Mail Server'  
yum -y groupremove --skip 'Network Servers'  
yum -y groupremove --skip 'System Tools'  
yum -y groupremove --skip 'Text-based Internet'  
yum -y groupremove --skip 'Web Server'  
yum -y groupremove --skip 'Windows File Server'  

yum install -y nano

yum -y update

yum -y groupinstall --skip core  
yum -y groupinstall --skip base

yum -y install make
yum -y install mailx
yum -y install httpd gcc glibc glibc-common gd gd-devel php mysql-server mysql yum-priorities mod_dav_svn subversion

service httpd start
service mysqld start

rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt
cd /opt/
wget http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.1-1.el5.rf.i386.rpm
rpm -K rpmforge-release-0.5.1-1.el5.rf.*.rpm
rpm -i rpmforge-release-0.5.1-1.el5.rf.*.rpm
yum -y check-update
yum -y install phpmyadmin
service httpd restart
cd /etc/yum.repos.d/
wget http://www.phillip-cooper.co.uk/centos/centos-asterisk.repo
wget http://www.phillip-cooper.co.uk/centos/centos-digium.repo
cd /opt/
yum -y check-update
yum -y install asterisk16 asterisk16-configs asterisk16-voicemail dahdi-linux dahd
mkdir /var/run/asterisk  
chown -R asterisk /var/run/asterisk  
chown -R asterisk /var/log/asterisk  
chown -R asterisk /var/lib/asterisk/moh  
chown -R asterisk /var/lib/php/session
sed -i "s/User apache/User asterisk/" /etc/httpd/conf/httpd.conf 
sed -i "s/Group apache/Group asterisk/" /etc/httpd/conf/httpd.conf 
sed -i "s/AllowOverride All/AllowOverride None/" /etc/httpd/conf/httpd.conf
yum -y install ntp
cp /usr/share/zoneinfo/Europe/London /etc/localtime
shutdown now -r