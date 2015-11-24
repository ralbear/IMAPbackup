#!/bin/bash
#
# Run backup from a comma separated list of users
#
# @author Ricardo Albear <ricardo.albear@albeguru.es>
# @date 24/11/2015
#
##
INPUT=$1
OLDIFS=$IFS
IFS=,
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read email pass
do
        #create a workdir with the name of the account
        mkdir $email
        #create a log file
        touch backup_report.log
        #run the backup
        ./imapgrab.py -d -v -M -f $email -s server.domain.com -p 143 -u $email -p $pass -m "_ALL_,-INBOX.Trash,-INBOX.Spam" -L manager >> $email/backup_report.log
        #tar the backup files
        tar -czf done/$email.tar.gz $email/*
        #remove the workdir
        rm -r $email

done < $INPUT
IFS=$OLDIFS
