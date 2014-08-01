#!/usr/bin/expect
set timeout -1
set name [lindex $argv 0]
set user [lindex $argv 1]
set password [lindex $argv 2]
spawn telnet $name
expect "User Name : "
send "$user\r"
sleep 1
expect "Password  : "
send "$password\r"
sleep 1
expect "> "
send "2\r"
sleep 1
expect "> "
send "8\r"
sleep 1
expect "> "
send "1\r"
sleep 1
expect "> "
send "1\r"
sleep 1
expect "> "
send "1\r"
sleep 1
expect "> "
send "3\r"
sleep 1
expect "> "
send "\x1b\r"
sleep 1
expect "> "
send "\x1b\r"
sleep 1
expect "> "
send "\x1b\r"
sleep 2
expect "> "
send "\x1b\r"
sleep 2
expect "> "
send "4\r"
sleep 3
send "\r"
