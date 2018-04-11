# l8r - snooze email via IMAP
#
# Copyright 2018 Aaron Oppenheimer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Assumes Python 3 environment

import imaplib
import email
from datetime import datetime, timezone
from dateutil import parser
from dateutil.relativedelta import *
import os

encrypted_credentials=True # set true if you're not using encryption
if encrypted_credentials:
	# if you are using encrypted environment variables in Lambda, here's where they get decrypted:
	import boto3
	from base64 import b64decode
	ENCRYPTED_p = os.environ['l8rPassword']
	DECRYPTED_p = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_p))['Plaintext']

	ENCRYPTED_s = os.environ['l8rServer']
	DECRYPTED_s = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_s))['Plaintext']

	ENCRYPTED_u = os.environ['l8rUser']
	DECRYPTED_u = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_u))['Plaintext']


# These are the definitions of the mailboxes and the criteria for whether to move their contents
# back to the inbox. In the original, the script should run twice/day, so the "tomorrow" box
# passes every morning, and the "tonight" box passes every night.
boxes = {
	'l8r/tonight' : datetime.now(timezone.utc).hour >= 12,
	'l8r/tomorrow' : datetime.now(timezone.utc).hour < 12,
	'l8r/next week' : (datetime.today().weekday() == 0) and (datetime.now(timezone.utc).hour < 12),
	'l8r/weekend' : (datetime.today().weekday() == 5) and (datetime.now(timezone.utc).hour < 12),
	'l8r/next month' : (datetime.today().day == 1) and (datetime.now(timezone.utc).hour < 12),
}

# If there's a mailbox in the "boxes" dictionary with the correct name, process it
def processMailbox(obj, boxname):
	if boxname in boxes.keys():
		# process everything in this mailbox
		typ, count = obj.select('"{0}"'.format(boxname))
		count = int(count[0])
		print('{0} has {1} messages'.format(boxname, count))
		to_copy = range(1, count+1)
		doCopy(obj, to_copy)

# copy everything in "to_copy" back to the inbox. "to_copy" is just a list of message indices.
def doCopy(obj, to_copy):
	if to_copy:
		copyset = ','.join([str(x) for x in to_copy])

		# set unread
		typ,data = obj.store(copyset, '-FLAGS', '\\Seen')

		# copy to inbox
		typ,data = obj.copy(copyset,"INBOX")

		# delete from this mailbox
		typ,data = obj.store(copyset, '+FLAGS', '\\Deleted')

		# make it go away
		typ,data = obj.expunge()


# log into the mail account and process everything in the "boxes" dict.
# Pass in "usefule" if running from a shell and there's a password file. Otherwise
# assumes environment variables for use in AWS Lambda.
#
# Password file has three lines:
#   <server> (e.g. imap.foo.bar)
#   <mailbox name>
#   <mailbox password>
#
def main(usefile=False):

	if usefile:
		try:
			with open("pwd.txt") as f:
				s = f.readline().strip()
				u = f.readline().strip()
				p = f.readline().strip()
		except:
			print("could not open password file")
			exit(-1)
	else:
		if encrypted_credentials:
			s = DECRYPTED_s.decode('UTF-8')
			u = DECRYPTED_u.decode('UTF-8')
			p = DECRYPTED_p.decode('UTF-8')
		else:
			s = os.environ["l8rServer"]
			u = os.environ["l8rUser"]
			p = os.environ["l8rPassword"]

	try:
		obj = imaplib.IMAP4_SSL(s, 993)
		obj.login(u,p)
	except:
		print("could not log in to server")
		exit(-1)

	for mb in boxes.keys():
		print('processing mailbox',mb)
		processMailbox(obj,mb)


def lambda_handler(event, context):
    main(usefile=False)
    return 'done!'

if __name__ == "__main__":
	main(usefile=True)
