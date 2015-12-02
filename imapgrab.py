#!/usr/bin/env python

# IMAP Grab
# Version 0.1.4
ig_version_short="0.1.5"

# Copyleft:
#   This program was first written by Daniel Roesler (diafygi) in
#   January 2009. It is released under the Gnu Public License v2
#   (GPLv2) as Free Software. Enjoy.
#   <http://www.gnu.org/licenses/gpl-2.0.txt>
# Contact:
#   diafygi [curvy thing] gmail [period] com
#   <http://daylightpirates.org/>

# Description:
#   imapgrab is a program that allows you to log into an IMAP server
#   and download selected mailboxes (i.e. folders/labels) to mbox or
#   maildir files.
#   You can also list the folders on that server. It is basically a
#   wrapper for getmail (a mail downloading program). When done
#   downloading selected mailboxes, you end up with one .mbox file
#   or maildir folder per mailbox.
# Features:
#   -Mbox or Maildir download formats, Mbox by default
#   -SSL connections possible
#   -multiple select mailboxes may be downloaded in one command
#   -all available folders may be downloaded
#   -folders may be excepted when above is enabled
#   -when mbox file is detected, only new mail is downloaded, but
#     this can be changed (with -a)
#   -special option to except Google Mail (Gmail) folders from download
# Dependancies:
#   getmail 4.8.2 or higher
#   python 2.5.2 or higher

# Usage:
#  imapgrab.py [-ldaSvMB] [-s] SERVER [-P] PORT [-u] USERNAME [-p] PASSWORD [-m] "BOX1,BOX2,..." [-f] DIRECTORY
#    Possible arguments:
#    --list, -l        List the mailboxes available for download
#    --download, -d    Download mailboxes to separate files/folders
#    --mbox, -B        Download into Mbox format (optional, default)
#    --maildir, -M     Download into Maildir format (optional)
#    --all, -a         Force download all mail in a mailbox (optional)
#    --ssl, -S         Use SSL connection (optional)
#    --server, -s      IP or domain of server (required)
#    --port, -P        Port of server (optional)
#    --username, -u    Username for account (required)
#    --password, -p    Password for account (required)
#    --mailboxes, -m   Comma separated list of mailboxes to download
#                       (i.e. "Box1, Box2, Box3")
#                       ("{,}" for non-separating commas)
#                       ("_ALL_" for all mailboxes)
#                       ("_ALL_, -Box1" to except Box1 from _ALL_)
#                       ("_ALL_, -_Gmail_" to except [Gmail]* and [Google Mail]* folders)
#                       ("_Gmail_" for all [Gmail]/* or [Google Mail]/* folders)
#                       (required for -d)
#    --folder, -f      Path to folder
#                       (optional, creates imapgrab folder in current directory as default)
#    --localuser, -L   User that writes to the mailboxes
#                       (use only when involking imapgrab as root)
#    --quiet, -q       Don't display any output
#    --verbose, -v     Verbose output
#    --debug           Print debug output
#    --version         Print version
#    --about           Display detailed info
#    --help, -h        Print help with command options

# Examples:
#  1) List available mailboxes
#       imapgrab.py -l -s imap.example.com -u username -p password
#  2) Download "box1" and "box2" from server imap.example.com (save "box1.mbox" and "box2.mbox")
#       imapgrab.py -d -s imap.example.com -u username -p password -m "box1, box2"
#  3) Download all mailboxes except "box3"
#       imapgrab.py -d -s imap.example.com -u username -p password -m "_ALL_, -box3"
#  4) Download all Gmail custom labels and INBOX (none of the [Gmail]* mailboxes)
#       imapgrab.py -d -S -s imap.gmail.com -u username -p password -m "_ALL_, -_Gmail_"
#  5) Download Gmail label "receipts"
#       imapgrab.py -d -S -s imap.gmail.com -u username -p password -m "receipts"

from optparse import OptionParser
import imaplib
import os
import copy
import subprocess

ig_version_long="imapgrab " + ig_version_short
ig_about="IMAP Grab - Version " + ig_version_short + "\nWritten by Daniel Roesler (diafygi)\nReleased under GNU Public License v2\n<http://www.gnu.org/licenses/gpl-2.0.txt>"

def imapgrab():
  ig_cmd = OptionParser(usage="%prog [-ldaSv] [-s] SERVER [-P] PORT [-u] USERNAME [-p] PASSWORD [-m] \"BOX1,BOX2,...\" [-f] DIRECTORY",
                        description="Description: ImapGrab connects to a imap server and downloads mail from selected mailboxes to mbox files. Released under GPLv2.")
  ig_cmd.add_option("-l", "--list", action="store_true", help="List the mailboxes available for download")
  ig_cmd.add_option("-d", "--download", action="store_true", help="Download mailboxes to separate files/folders")
  ig_cmd.add_option("-B", "--mbox", action="store_true", help="Download into Mbox format (optional, default)")
  ig_cmd.add_option("-M", "--maildir", action="store_true", help="Download into Maildir format (optional)")
  ig_cmd.add_option("-a", "--all", action="store_true", help="Force download all mail in a mailbox (optional)")
  ig_cmd.add_option("-S", "--ssl", action="store_true", help="Use SSL connection (optional)")
  ig_cmd.add_option("-s", "--server", dest="server", help="IP or domain of server (required)")
  ig_cmd.add_option("-P", "--port", dest="port", help="Port of server (optional)")
  ig_cmd.add_option("-u", "--username", dest="username", help="Username for account (required)")
  ig_cmd.add_option("-p", "--password", dest="password", help="Password for account (required)")
  ig_cmd.add_option("-m", "--mailboxes", dest="mailboxes", help="Comma separated list of mailboxes to download (i.e. \"Box1, Box2, Box3\") ('{,}' for non-separating commas) ('_ALL_' for all mailboxes, '-Box1' to except Box1 from _ALL_) (required for -d)")
  ig_cmd.add_option("-f", "--folder", dest="folder", help="Path to folder (optional, creates imapgrab folder in current directory as default)")
  ig_cmd.add_option("-L", "--localuser", dest="localuser", help="User that writes to the mailboxes. (only use when invoking imapgrab as root)")
  ig_cmd.add_option("-q", "--quiet", action="store_true", help="Don't display any output")
  ig_cmd.add_option("-v", "--verbose", action="store_true", help="Verbose output")
  ig_cmd.add_option("--debug", action="store_true", help="Print debug output")
  ig_cmd.add_option("--version", action="store_true", help="Print version")
  ig_cmd.add_option("--about", action="store_true", help="Display detailed info")
  (ig_options, ig_args) = ig_cmd.parse_args()

  #debug shows parsed command
  if(ig_options.debug is True):print "DEBUG_000: parsed options:\n",ig_options,"\nDEBUG: parsed arguments:\n",ig_args

  #verbose shows title
  if(ig_options.quiet is not True and ig_options.version is not True and ig_options.about is not True):
    print "IMAP Grab "+ig_version_short+"\n---"

  #show version number
  if ig_options.version is True:
    if(ig_options.debug is True):print "DEBUG_001: printing version number"
    if(ig_options.verbose is True):print "Printing version number:"
    print ig_version_long

  #show about display
  elif ig_options.about is True:
    if(ig_options.debug is True):print "DEBUG_002: printing about display"
    if(ig_options.verbose is True):print "Printing about display:"
    print ig_about

  #check for list or download
  elif (ig_options.list is True) or (ig_options.download is True):

    #ERROR if both list and download are used
    if (ig_options.list is True) and (ig_options.download is True):
      if(ig_options.debug is True):print "DEBUG_003: both -l and -d were parsed"
      if(ig_options.verbose is True):print "Both -l and -d were parsed"
      print "ERROR: Cannot list mailboxes (--list or -l) and download backup (--download or -d) at the same time."

    #ERROR if username/password/server
    elif ig_options.username is None: print "ERROR: No username set (--username or -u)"
    elif ig_options.password is None: print "ERROR: No password set (--password or -p)"
    elif ig_options.server is None: print "ERROR: No server set (--server or -s)"

    #--list, call list function
    elif ig_options.list is True:
      if(ig_options.debug is True):print "DEBUG_004: -l parsed, calling list function"
      if(ig_options.verbose is True):print "List option selected"
      ig_list = IG_list_mailboxes(ig_options)
      if(ig_options.quiet is not True):print "List of mailboxes available:"
      for i in ig_list:
        print i

    #--download, call download function
    elif ig_options.download is True:
      if(ig_options.debug is True):print "DEBUG_005: -d parsed, calling download function"
      if(ig_options.verbose is True):print "Download option selected"
      IG_backup_mail(ig_options)

  #ERROR and show help
  else:
    if(ig_options.debug is True):print "DEBUG_006: no options entered"
    print "Needs --list or --download option."
    ig_cmd.print_help()

  return True


#FUNCTION- LIST MAILBOXES
def IG_list_mailboxes(ig_options):
  #Open IMAP connection
  if ig_options.ssl is True:
    if(ig_options.debug is True):print "DEBUG_007: -S parsed, connecting via SSL"
    if(ig_options.verbose is True):print "Connecting to IMAP server via SSL"
    if ig_options.port is None:
      ig_options.port = 993
    else:
      ig_options.port = int(ig_options.port)
    ig_imap = imaplib.IMAP4_SSL(ig_options.server, ig_options.port)
  else:
    if(ig_options.debug is True):print "DEBUG_008: no -S parsed, connecting with no SSL"
    if(ig_options.verbose is True):print "Connecting to IMAP server"
    if ig_options.port is None:
      ig_options.port = 143
    else:
      ig_options.port = int(ig_options.port)
    ig_imap = imaplib.IMAP4(ig_options.server, ig_options.port)

  #Login to IMAP Server
  if(ig_options.debug is True):print "DEBUG_010: sending username/password to server"
  if(ig_options.verbose is True):print "Logging into IMAP server"
  ig_imap.login(ig_options.username,ig_options.password)
  if(ig_options.debug is True):print "DEBUG_011: connected to IMAP server"

  #Get mailboxes list
  ig_list_raw = []
  ig_list = []
  imap_list = ig_imap.list("")
  #print ig_imap.status("mailbox", "(MESSAGES)")   #Returns number of messages in a mailbox, maybe I'll use it later
  if(ig_options.debug is True):
    print "DEBUG_012: got list of mailboxes:"
    print imap_list
  #Parses out mailbox names from other metadata
  for i in imap_list[1]:
    ig_list_raw.append(i.split('" ',1)[1])
  #Removes surrounding quotations if they exist
  for i in ig_list_raw:
    if i[0] == "\"" and i[len(i)-1] == "\"":
      ig_list.append(i[1:len(i)-1])
    else:
      ig_list.append(i)

  #Logout of IMAP server
  ig_imap.logout()
  if(ig_options.debug is True):print "DEBUG_013: logged out of server"
  return ig_list

#FUNCTION- BACKUP MAIL
def IG_backup_mail(ig_options):
  #Remove verbose/debug options for list function call
  ig_list_options = copy.copy(ig_options)
  ig_list_options.debug = None
  ig_list_options.verbose = None

  #Call list function
  if(ig_options.verbose is True):print "Getting list of mailboxes"
  if(ig_options.debug is True):print "DEBUG_014: getting list of mailboxes:"
  ig_list = IG_list_mailboxes(ig_list_options)
  if(ig_options.debug is True):print ig_list

  #Set default port
  if ig_options.port is None and ig_options.ssl is True:
    ig_options.port = "993"
  if ig_options.port is None and ig_options.ssl is None:
    ig_options.port = "143"

  #Error if no list of mailboxes
  if ig_options.mailboxes is None:
    print "ERROR: no mailboxes selected for download (use -m or --mailboxes option)"
    return

  #Create list from -m
  ig_download_str_rm_comma = ig_options.mailboxes.replace("{,}","<!comma!>")
  if(ig_options.debug is True): print "DEBUG_015: removed non-separating commas: \"" + ig_download_str_rm_comma + "\""
  ig_download_list_raw = ig_download_str_rm_comma.split(",")
  ig_download_list_fix_comma = []
  for i in ig_download_list_raw:
    ig_download_list_fix_comma.append(i.replace("<!comma!>",","))
  ig_download_list = []
  for i in ig_download_list_fix_comma:
    ig_download_list.append(i.strip())

  #Gmail exceptions
  gmail_list = ['[Gmail]','[Gmail]/All Mail', '[Gmail]/Drafts', '[Gmail]/Sent Mail', '[Gmail]/Spam', '[Gmail]/Starred', '[Gmail]/Trash',
    '[Google Mail]', '[Google Mail]/All Mail', '[Google Mail]/Drafts', '[Google Mail]/Sent Mail', '[Google Mail]/Spam', '[Google Mail]/Starred', '[Google Mail]/Trash']

  #Work out exceptions for _ALL_
  if "_ALL_" in ig_download_list:
    ig_exceptions_list = []
    for i in ig_download_list:
      if i == "-_Gmail_":
        for j in gmail_list:
          ig_exceptions_list.append(j)
      elif i[0] is "-":
        ig_exceptions_list.append(i[1:])
    ig_download_list = filter(lambda x:x not in ig_exceptions_list,ig_list)

  #Work out exceptions for _Gmail_
  if "_Gmail_" in ig_download_list:
    ig_download_list.remove("_Gmail_")
    if "[Gmail]" in ig_list:
      for i in gmail_list[1:7]:
        ig_download_list.append(i)
    elif "[Google Mail]" in ig_list:
      for i in gmail_list[8:14]:
        ig_download_list.append(i)
    else:
      print "ERROR: Gmail doesn't appear to be in your list of mailboxes"

  #Remove duplicates from download list
  ig_download_list = sorted(set(ig_download_list))

  #Compare list from -m to available mailboxes
  if(ig_options.verbose is True):
    print "List of mailboxes selected to download:"
    print ig_download_list
  if(ig_options.debug is True):
    print "DEBUG_017: List of mailboxes to download:"
    print ig_download_list
  if(ig_options.debug is True): print "DEBUG_018: checking -m list against available mailboxes on server"
  if(ig_options.verbose is True): print "Checking available mailboxes on server"
  ig_all_found = []
  for i in ig_download_list:
    for n in ig_list:
      if i == n:
        ig_all_found.append(i)
  if len(ig_all_found) != len(ig_download_list):
    print "ERROR: The following mailboxes weren't available:"
    print filter(lambda x:x not in ig_all_found, ig_download_list)
    print "ERROR: Some of the mailboxes you selected are not available for download. Use list option (-l or --list) to see availabe mailboxes."
    return
  if(ig_options.debug is True):print "DEBUG_019: found all items in -m"

  #Create directory for storage
  if ig_options.folder is None:
    ig_options.folder = os.getcwd() + os.sep + "imapgrab"
    if(ig_options.debug is True):print "DEBUG_020: no -f parsed, using current directory: " + ig_options.folder + os.sep + "imapgrab"
  #Remove last slash if it exists
  elif ig_options.folder[-1] is os.sep:
    ig_options.folder = ig_options.folder[0:(len(ig_options.folder)-1)]

  #Check to see if directory exists
  if os.path.exists(ig_options.folder) is not True:
    #Make folder path from root
    if(ig_options.folder[0] is not os.sep):
      ig_options.folder = os.getcwd() + os.sep + ig_options.folder
    if(ig_options.debug is True):print "DEBUG_021: folder does not exist, creating new folder in " + ig_options.folder
    if(ig_options.verbose is True):print "Creating folder for backup"
    os.makedirs(ig_options.folder)
  else:
    if(ig_options.debug is True):print "DEBUG_022: directory already exists"

  #Create rc files for getmail
  if(ig_options.debug is True):print "DEBUG_023: creating rc files for getmail"
  if(ig_options.verbose is True):print "Creating download config files in " + ig_options.folder
  for i in ig_download_list:

    #Create needed folders
    if os.sep in i:
      folders = i.split(os.sep)
      filename = folders[-1]
      fpath = ig_options.folder
      #Check to see if folder exists, create if not
      for f in range(0,len(folders)-1):
        fpath = fpath + os.sep + folders[f]
        if os.path.exists(fpath) is not True:
          if(ig_options.debug is True):print "DEBUG_024: creating \"" + folders[f] + "\" folder since it doesn't exist"
          if(ig_options.verbose is True):print "\"" + folders[f] + "\" folder doesn't exist, creating folder"
          os.mkdir(fpath)
    else:
      fpath = ig_options.folder
      filename = i

    #Open file
    rc_file = open(fpath + os.sep + filename + ".rc", "w")

    #Write config lines to file
    rc_file.write("[retriever]\n")
    if ig_options.ssl is True:
      rc_file.write("type = SimpleIMAPSSLRetriever\n")
    else:
      rc_file.write("type = SimpleIMAPRetriever\n")
    rc_file.write("server = " + ig_options.server + "\n")
    rc_file.write("port = " + ig_options.port + "\n")
    rc_file.write("username = " + ig_options.username + "\n")
    rc_file.write("password = " + ig_options.password + "\n")
    rc_file.write("mailboxes = (\"" + i + "\",)\n\n")
    rc_file.write("[destination]\n")
    if ig_options.localuser is not None:
      rc_file.write("user = " + ig_options.localuser + "\n")
    if ig_options.maildir is True:
      rc_file.write("type = Maildir\n")
      rc_file.write("path = " + fpath + os.sep + filename + os.sep + "\n\n")
    else:
      rc_file.write("type = Mboxrd\n")
      rc_file.write("path = " + fpath + os.sep + filename + ".mbox\n\n")
    rc_file.write("[options]\n")
    if ig_options.all is not True:
      rc_file.write("read_all = false\n")
    if ig_options.debug is True:
      rc_file.write("verbose = 2\n")

    #Close file
    rc_file.close()
    #Debug/Verbose explainations
    if(ig_options.verbose is True):print "Created \"" + fpath + os.sep + filename + ".rc\""
    if(ig_options.debug is True):
      print "DEBUG_024: Contents of \"" + fpath + os.sep + filename + ".rc\":"
      print "--------------------"
      print open(fpath + os.sep + filename + ".rc", "r").read()
      print "--------------------"

    if ig_options.maildir is True:
      #Create maildir directory if doesn't exist
      maildir_directories = ["", "new"+os.sep, "cur"+os.sep, "tmp"+os.sep]
      for f in maildir_directories:
        if os.path.isdir(fpath + os.sep + filename + os.sep + f) is not True:
          if(ig_options.verbose is True):print "Maildir directory doesn't exist, creating \"" + fpath + os.sep + filename + os.sep + f + "\""
          if(ig_options.debug is True):print "DEBUG_025: \"" + fpath + os.sep + filename + os.sep + f + "\" doesn't exist, creating"
          os.mkdir(fpath + os.sep + filename + os.sep + f)
        else:
          if(ig_options.verbose is True):print "Maildir directory already exists, using \"" + fpath + os.sep + filename + os.sep + f + "\""
          if(ig_options.debug is True):print "DEBUG_026: \"" + fpath + os.sep + filename + os.sep + f + "\" exists"
    else:
      #Create mbox file if doesn't exist
      if os.path.isfile(fpath + os.sep + filename + ".mbox") is not True:
        if(ig_options.verbose is True):print "Mbox file doesn't exist, creating \"" + fpath + os.sep + filename + ".mbox\""
        if(ig_options.debug is True):print "DEBUG_025: \"" + fpath + os.sep + filename + ".mbox\" doesn't exist"
        open(fpath + os.sep + filename + ".mbox", "w").close()
      else:
        if(ig_options.verbose is True):print "Mbox file already exists, using \"" + fpath + os.sep + filename + ".mbox\""
        if(ig_options.debug is True):print "DEBUG_026: \"" + fpath + os.sep + filename + ".mbox\" exists"

  #Call getmail command
  for mailbox in ig_download_list:

    #Build folder path to .rc files created previously
    if os.sep in mailbox: #Check to see if there are folders in mailbox name
      folders = mailbox.split(os.sep)
      filename = folders[-1]
      path_from_folder = ""
      for f in range(0,len(folders)-1): #Add folder path in mailbox name
        path_from_folder = path_from_folder + os.sep + folders[f]
    else:
      path_from_folder = ""
      filename = mailbox

    #Set getmail command and options for getmail command
    cmd = "getmail"
    rc_file_loc = path_from_folder + os.sep + filename + ".rc"
    #Remove first os.sep
    rc_file_loc = rc_file_loc[1:]

    #Set local user permissions if needed
    if ig_options.localuser is not None:
      #######Can't use os.chown() because it's not recursive...unless there's something I don't know.#############
      os.system( "chown -R " + ig_options.localuser + " " + ig_options.folder)

    #Call getmail command
    if(ig_options.verbose is True):print "Calling getmail to retrieve mail for mailbox \"" + ig_options.folder + os.sep + path_from_folder + os.sep + filename + "\""
    if(ig_options.quiet is not True):print "Downloading mailbox \"" + mailbox + "\""
    if(ig_options.debug is True):print "DEBUG_027: calling \"" + cmd + " -g " + ig_options.folder + " -r " + rc_file_loc + "\""
    if ig_options.verbose is True or ig_options.debug is True:
      subprocess.call([cmd, "-g", ig_options.folder, "-r", rc_file_loc])
    else:
      subprocess.call([cmd, "--quiet", "-g", ig_options.folder, "-r", rc_file_loc])
    os.remove(ig_options.folder + os.sep + rc_file_loc)

  #Print complete
  if(ig_options.quiet is not True):print "Downloads complete"

if __name__ == "__main__":
  imapgrab()
