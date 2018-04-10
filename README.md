# l8r
Tools for snoozing email.

Ever wish you could make an email disappear from your inbox, and have it return later? Some email systems give you that feature,
but most don't. l8r works with any imap email system to give basic snoozin'.

### Theory of Operation

It's not just a theory. l8r requires you to set up specific mailboxes, and run a script a couple of times a day. Those mailboxes have names _tonight_, _tomorrow_, _weekend_, and _next week_. When you want to snooze an email, just file it into one of those boxes. When the script runs, it will check to see if it should move the mail in that folder back into the inbox. That's it! When the script runs in the morning, it will move anything in the _tomorrow_ box; when it runs in the afternoon, it will move anything in the _tonight_ box. If it's Saturday or Monday, the _weekend_ or _next weekend_ boxes will be processed.

### Mailboxes

l8r expects you to set up a _l8r_ mailbox with sub-mailboxes _tonight_, _tomorrow_, _weekend_, and _next week_. The _l8r_ box itself isn't processed.

### Script

The l8r script should be run twice per day. For example, 6am and 6pm, to process the _tomorrow_ and _tonight_ boxes, respectively. The script can be run from a shell, or from a service like AWS Lambda.

If run inside Lambda, use CloudWatch events to schedule the runs.

The morning run cron statement:
```cron(0 11 * * ? *)```

The afternoon run cron statement:
```cron(0 22 * * ? *)```

Note that Lambda assumes GMT so both the script and cron should take that into account.

### Credentials

l8r needs a server, email account, and password. This can be managed using a configuration file local to the script, or Lambda environment variables.

If running the script from a shell, create a file called 'pwd.txt' in the same directory with three lines:

~~~~
  <server address e.g. imap.foo.com>
  <email address e.g. aaron@aoppenheimer.com>
  <email password e.g. thisismypassword>
~~~~

If running the script in Lambda, create three environment variables to hold the information:

~~~~
  l8rServer
  l8rUser
  l8rPassword
~~~~

If you like, you can use the key manager to encrypt the environment variables and decrypt them in the script; if you choose not to do this, change the script to make plaintext=True.

### Enjoy

Feel free to change whatever you want. l8r is licensed under GPLv3.

Reach me at aaron@aoppenheimer.com


