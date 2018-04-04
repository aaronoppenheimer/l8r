import imaplib
import email
import datetime
from dateutil import parser
from dateutil.relativedelta import *
from datetime import timezone
import os

boxes = {
	'l8r/tomorrow' : relativedelta(days=1),
	'l8r/next week' : relativedelta(days=1, weekday=MO),
}


def processMailbox(obj, boxname):
	typ, count = obj.select('"{0}"'.format(boxname))
	count = int(count[0])
	print('{0} has {1} messages'.format(boxname, count))

	to_copy = []
	for i in range(count):

		typ, data = obj.fetch(str(i+1),"(UID RFC822)")
		if typ != 'OK':
			print("ERROR getting message", i)
			return

		# print(data[0][1].decode('UTF-8'))
		msg = email.message_from_string(data[0][1].decode('UTF-8'))
		date = parser.parse(msg['Date'])

		now = datetime.datetime.now()
		now = now.replace(tzinfo = date.tzinfo)

		tomorrow = (date + boxes[boxname]).replace(hour=5,minute=0,second=0)

		print('now',now)
		print('date', date)
		print('tomorrow',tomorrow)

		subject = msg['Subject']

		if now > tomorrow:
			print('do it!')
			to_copy.append(i+1)
		else:
			print('not yet')

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
