#!/usr/bin/env python
#
# Description: Script to collect system DMI information for asset management.
# Author: Sumit Goel <sumit.goel@salesforce.com>
#

import sys
try:
	import xmlrpclib
	import csv
	import time
	import os
	import smtplib
	from email.MIMEMultipart import MIMEMultipart
	from email.MIMEBase import MIMEBase
	from email.MIMEText import MIMEText
	from email import Encoders
except ImportError, e:
	print 'ImportError:', e
	sys.exit(1)

SATELLITE_URL = "http://localhost/rpc/api"
CREDENTIALS = open("/root/.sfdcdeploycreds", "r")
try:
	LINE = ((CREDENTIALS.readline()).rstrip()).split(":")
	SATELLITE_LOGIN = LINE[0]
	SATELLITE_PASSWORD = LINE[1]
finally:
	CREDENTIALS.close()

CLIENT = xmlrpclib.Server(SATELLITE_URL, verbose=0)
KEY = CLIENT.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
ALLACTIVESYSTEMS = CLIENT.system.listActiveSystems(KEY)

FILENAME = "systems_dmi_report_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
OUTFILEPATH = "/tmp/" + FILENAME
OPENFILE = open(OUTFILEPATH, 'wb')
CSVFILE = csv.writer(OPENFILE,quoting=csv.QUOTE_ALL)
CSVFILE.writerow(['Server Name','Vendor','Product','Asset'])

for ITEM in ALLACTIVESYSTEMS:
	SYSTEMID = ITEM['id']
	SYSTEMNAME = ITEM['name']
	SYSTEMDMI = CLIENT.system.getDmi(KEY,SYSTEMID)
	try:
		CSVFILE.writerow([SYSTEMNAME, SYSTEMDMI['vendor'], SYSTEMDMI['product'], SYSTEMDMI['asset']])
	except csv.Error, e:
		print "Error:", e

OPENFILE.close()
CLIENT.auth.logout(KEY)

EMAIL_FROM = "Sumit Goel <sumit.goel@salesforce.com>"
EMAIL_TO = ["sumit.goel@salesforce.com"]
EMAIL_SUBJECT = "RHEL Systems DMI Information for the month of " + time.strftime("%B %Y")
EMAIL_BODY = "Please find attachment."

MESSAGE = MIMEMultipart()
MESSAGE['Subject'] = EMAIL_SUBJECT
MESSAGE['From'] = EMAIL_FROM
MESSAGE['To'] = ', '.join(EMAIL_TO)
MESSAGE.attach(MIMEText(EMAIL_BODY))

ATTACHMENT = MIMEBase('application', "octet-stream")
ATTACHMENT.set_payload(open(OUTFILEPATH, "rb").read())
Encoders.encode_base64(ATTACHMENT)
ATTACHMENT.add_header('Content-Disposition', 'attachment', filename=FILENAME)

MESSAGE.attach(ATTACHMENT)

MAILER = smtplib.SMTP()
MAILER.connect()
MAILER.sendmail(EMAIL_FROM, EMAIL_TO, MESSAGE.as_string())
MAILER.close()

os.remove(OUTFILEPATH)

#
#EOF
