import imaplib
import email
import datetime
from dateutil import parser
from dateutil.relativedelta import *
from datetime import timezone

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




	typ, count = obj.select('l8r')
	count = int(count[0])
	print('l8r has {0} messages'.format(count))

	tocopy = []
	for i in range(count):

		typ, data = obj.fetch(str(i+1),"(FLAGS)")
		if typ != 'OK':
			print("ERROR getting message", i)
			return
		print('flags:',data)

		typ, data = obj.fetch(str(i+1),"(UID RFC822)")
		if typ != 'OK':
			print("ERROR getting message", i)
			return

		# print(data[0][1].decode('UTF-8'))
		msg = email.message_from_string(data[0][1].decode('UTF-8'))
		print(msg['Date'])
		date = parser.parse(msg['Date'])

		now = datetime.datetime.now() + date.utcoffset()
		now = now.replace(tzinfo = date.tzinfo)

		tomorrow = (date + relativedelta(days=1)).replace(hour=7,minute=0,second=0)

		subject = msg['Subject']
		print(i, date, subject)

		if now > (date + relativedelta(days=1)):
			print('do it!')
			tocopy.append(i+1)
		else:
			print('not yet')

	if tocopy:
		copyset = ','.join([str(x) for x in tocopy])

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

if __name__ == "__main__":
	main()
