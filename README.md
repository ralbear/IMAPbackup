# Backup remote IMAP server #

After spending some time looking for a simple and reliable solution to backup a whole IMAP server, I have created this script to automate it from a comma separated files.

This script backup the whole messages and folders and returns a compressed file named as the user account user@domain.com.tar.gz, also including a log of the backup

## Table of contents ##
- [Previous requirements](#previous-requirements)
- [Comma separated data source](#comma-separated-data-source)
- [Customize server details](#customize-server-details)
- [References](#references)

## Previous requirements ##

- python 2.3.3 or later
- getmail

If you are running an Ubuntu/Debian system you can install this running:

```Shell
$ sudo apt-get install python getmail4
```
Move to a work directory, clone this repository and change execution permission of the files
```Shell
$ sudo chmod +x imapgrab.py run.sh
```
To test the connection with the server and list the folders for an account can do this

```Shell
$ ./imapgrab.py -l -s server.domain.com -S -p 993  -u username -p password
```

## Comma separated data source ##
The file with the account´s details must look like this.
```Shell
user1@domain.com,password1
user2@domain.com,password2
```

## Customize server details ##
In the line 20 of `run.sh` file we can customize some details
```Shell
./imapgrab.py -d -v -M -f $email -s server.domain.com -p 143 -u $email -p $pass -m "_ALL_,-INBOX.Trash,-INBOX.Spam" -L manager >> $email/backup_report.log
```
**mbox or maildir**

`-M` for maildir (default)

`-B` for mailbox

**Server name**

`server.domain.com` this is the name of the server

**Port and SSL**

`-p 143` connection port

`-S -p 993` add `-S` before port in case of a SSL connection

**Skip some folders**

`-m "_ALL_,-INBOX.Trash,-INBOX.Spam"` copy all the folders except *INBOX.Trash* and *INBOX.Spam*

**Alternative user needed**

`-L manager` if you run this script as *root* you need an alternative user to run *imapgrab*, in this case i have create manager user

## References ##
 - [Imapgrab project](http://sourceforge.net/projects/imapgrab/)
 - [Dmitri Popov](https://github.com/dmpop) **-** [Back-up-Email-with-a-Single-Command](http://www.linux-magazine.com/Online/Blogs/Productivity-Sauce/Back-up-Email-with-a-Single-Command)
