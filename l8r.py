import imaplib
import email
import datetime
from dateutil import parser
from dateutil.relativedelta import *
from datetime import timezone


def processMailbox(obj, box):
	typ, count = obj.select(box)
	count = int(count[0])
	print('l8r has {0} messages'.format(count))

	to_copy = []
	for i in range(count):

		typ, data = obj.fetch(str(i+1),"(UID RFC822)")
		if typ != 'OK':
			print("ERROR getting message", i)
			return

		# print(data[0][1].decode('UTF-8'))
		msg = email.message_from_string(data[0][1].decode('UTF-8'))
		print(msg['Date'])
		date = parser.parse(msg['Date'])

		now = datetime.datetime.now()
		now = now.replace(tzinfo = date.tzinfo)

		tomorrow = (date + relativedelta(days=1)).replace(hour=7,minute=0,second=0)

		print('date', date)
		print('now',now)
		print('tomorrow',tomorrow)

		subject = msg['Subject']
		print(i, date, subject)

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


def main():

	try:
		with open("pwd.txt") as f:
			s = f.readline().strip()
			u = f.readline().strip()
			p = f.readline().strip()
	except:
		print("could not open password file")
		exit(-1)

	try:
		obj = imaplib.IMAP4_SSL(s, 993)
		obj.login(u,p)
	except:
		print("could not log in to server")
		exit(-1)


	# typ, count = obj.select('INBOX',True)
	# count = int(count[0])
	# for i in range(count):
	# 	typ, data = obj.fetch(str(i+1),"(FLAGS)")
	# 	print('flags:',data)
	# return		

	processMailbox(obj,'l8r')



if __name__ == "__main__":
	main()
