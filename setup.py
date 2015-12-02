#!/usr/bin/env python

from distutils.core import setup

setup(name='IMAPbackup',
      version='0.1.5',
      description='IMAP server backup',
      author='Matthew Wilkes',
      author_email='matt@matthewwilkes.name',
      url='https://github.com/MatthewWilkes/IMAPbackup',
      scripts=['imapgrab.py',]
)
