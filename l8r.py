import imaplib
import email
from datetime import datetime, timezone
from dateutil import parser
from dateutil.relativedelta import *
import os

boxes = {
	'l8r/tomorrow' : datetime.now(timezone.utc).hour < 12,
	'l8r/next week' : (datetime.today().weekday() == 0) and (datetime.now(timezone.utc).hour < 12),
	'l8r/weekend' : (datetime.today().weekday() == 5) and (datetime.now(timezone.utc).hour < 12),
	'l8r/tonight' : datetime.now(timezone.utc).hour >= 12,
}


def processMailbox(obj, boxname):

	if boxes[boxname]:
		# process everything in this mailbox
		typ, count = obj.select('"{0}"'.format(boxname))
		count = int(count[0])
		print('{0} has {1} messages'.format(boxname, count))

		to_copy = range(1, count+1)
		doCopy(obj, to_copy)


def doCopy(obj, to_copy):

	if to_copy:
		copyset = ','.join([str(x) for x in to_copy])

		# set unread
		typ,data = obj.store(copyset, '-FLAGS', '\\Seen')
		# print(typ,data)

		# copy to inbox
		typ,data = obj.copy(copyset,"INBOX")
		# print(typ,data)

		# delete from here
		typ,data = obj.store(copyset, '+FLAGS', '\\Deleted')
		# print(typ,data)

		# make it go away
		typ,data = obj.expunge()
		# print(typ,data)


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
		s = os.environ["l8rServer"]
		u = os.environ["l8rUser"]
		p = os.environ["l8rPassword"]

	try:
		obj = imaplib.IMAP4_SSL(s, 993)
		obj.login(u,p)
	except:
		print("could not log in to server")
		exit(-1)

	# typ, data = obj.list()
	# print(data)

	# typ, count = obj.select('INBOX',True)
	# count = int(count[0])
	# for i in range(count):
	# 	typ, data = obj.fetch(str(i+1),"(FLAGS)")
	# 	print('flags:',data)
	# return		

	for mb in boxes.keys():
		print('processing',mb)
		processMailbox(obj,mb)


def lambda_handler(event, context):
    main()
    return 'Hello from Lambda'


if __name__ == "__main__":
	main(usefile=True)
