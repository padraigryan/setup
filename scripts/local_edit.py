#!/usr/bin/env python
import os
import stat
import datetime
import sys
import pickle
import argparse
import shutil

"""
This script will do a chmod +w on a file for a local only edit and add it to a list of local edit across all workspaces.
With a single parameter of a file name, it will chmod +w that file and add it to the list of local edits. It will also 
create a copy of the file to compare against. Any string after
the file name will be considered a comment for reasons to lock that file.
With no parameters, it will parse the current list, check the r/w status of each file and update/display the file contents.


TODO:
5) Maintain some meta data about the file, when edit started etc.   - low priority
6) if WORKSPACE_NAME is not defined, work it out.
7) Revert a failed/aborted merge to the locally edited file
8) Save the depot file 
9) Handle multiple files of the same name in different workspace - use the current workspace

Done:

1) Handle files of the same name - prepends the workspace info
2) Create the list based on the current workspace only - prepends the workspace info
3) Create backups of before and after edits
4) Handle merging a file that has been updated.

fn : filename
ds : DateStamp
rf : restore file
com: comment
bf : backup file
"""

user = os.environ['USER']
try:
  workspace = os.environ['WORKSPACE_NAME']
except:
  print "Error: need to set WORKSPACE_NAME"
  os.exit()

local_edit_dir = "/home/" + user + "/.local_edits/"
#local_edit_dir = "/home/" + user + "/.local_edits_test/"
local_edit_list_fn = local_edit_dir + ".local_edit_filelist.pkl"
local_edits = []

def _init_read():

  if(os.path.isfile(local_edit_list_fn)):
   return pickle.load( open(local_edit_list_fn, "rb") )
  else:
    return []

def _get_ws_info_from_filename(filename):
  parts = filename.split('+')
  user_name = parts[0].split('/')[-1]
  ws_no = parts[3].split('/')[0]
  mini_prj = parts[1]
  variant = parts[2]
  return (user_name, mini_prj, variant, ws_no)

def display_list():
  global local_edits
  update_local_edits = []

  # Check if it's still writable.
  for (fn, date, ref_fn, comment) in local_edits:
    if(os.access(fn, os.W_OK) == True):
      update_local_edits.append( (fn, date, ref_fn, comment) )
    elif(os.path.exists(ref_fn)):
      print "INFO: Removing " + fn  + " from list of local edits"
      create_backup(ref_fn, "after")
      os.unlink(ref_fn)

  # Display the file for edit
  local_edits = update_local_edits
  if(len(local_edits) > 0):
    print "Locally edited files for : " + workspace
    (_d, _d, _d, cur_ws_no) =_get_ws_info_from_filename(workspace)
    print "{0:75}{1:40}{2:20}".format("File name", "Date", "Comment")
    for (fn, date, ref_fn, comment) in local_edits:
      (_d, _d, _d, fn_ws_no) = _get_ws_info_from_filename(fn)
      # Only display from current workspace and replace workspace name with $WORKSPACE
      if fn_ws_no == cur_ws_no:                                               
        end_of_ws = fn.find(fn_ws_no)
        fn = "$WORKSPACE" + fn[end_of_ws + len(fn_ws_no):]
        print "{0:75}{1:40}{2:20}".format(fn, date, comment)
  else:
    print "INFO: No files open for local edit"

  # Save the update
  pickle.dump(local_edits, open(local_edit_list_fn, "wb") )

def create_backup(file_name, bk_type):
  datestamp = datetime.datetime.now().strftime('/%Y%b%d_%H:%M:%S/')
  ref_dir = os.path.dirname(file_name)
  bk_dir  = local_edit_dir + bk_type + datestamp  + workspace + ref_dir.split(workspace)[-1]

  if not os.path.exists(bk_dir):
    os.makedirs(bk_dir)

  src  = file_name
  dest = bk_dir + '/' + os.path.basename(file_name)
  
  #print "INFO: Backup copy {} to {}".format(src, dest)
  shutil.copy(src, dest)
  
def add_new_file(file_name, comment=""):

  # Add the workspace to the file path.
  ref_fn =  local_edit_dir + workspace + file_name.split(workspace)[-1]
  ref_dir = os.path.dirname(ref_fn)

  # Change the writable permission
  if(os.access(file_name, os.W_OK)):
    print "WARN: " + file_name + " is already writable"
  else:
    os.system('chmod +w ' + file_name);

  # Create a local copy of the reference file
  if os.path.exists(ref_fn):
    print "WARN: Local edit file " + file_name + " was already available - overriding previous backup"
  else:
    if not os.path.exists(ref_dir):
      os.makedirs(ref_dir)
    shutil.copy(file_name, ref_fn)

  create_backup(file_name, "before")

  # Add it to the local edit file list
  date_stamp = "{0}".format(datetime.datetime.now().strftime("%A, %d %B %Y %I:%M%p"))
  local_edits.append(    (file_name, date_stamp, ref_fn, comment)    )
  pickle.dump(local_edits, open(local_edit_list_fn, "wb") )

def _search_local_edits(search_fn):
  possible_file = []
  for le in local_edits:
    (fn, ds, rfn, com) = le
    if(fn.find(search_fn) >= 0):
      possible_file.append(le)

  if(len(possible_file) == 0):
    print "ERROR: Couldn't find a file that looks like : " + search_fn
    sys.exit(-1)
  elif(len(possible_file) > 1):
    print "WARN: More than one possible match for " + search_fn + ":"
    for p in possible_file:
      print p
    for (fn, ds, rfn, com) in possible_file:
      if fn == search_fn:
        return (fn, ds, rfn, com)
  else:
    return possible_file[0]

def display_diff(fn):
  (fn, ds, rf, com) = _search_local_edits(fn)
  os.system('tkdiff ' + fn + ' ' + rf)

def sync_file(fn):
  local_file = _search_local_edits(fn)
  (fn, ds, rf, com) = local_file
  bf = rf + ".bk"

  # i.    create my backup of my local edited file.
  print "Backup of locally edited file : " + bf
  print "Restore file : " + rf
  print "Working file : " + fn
  shutil.copy(fn, bf)

  # ii.   remove writable status and sync that file - copy this as the new backup.
  os.system('chmod -w ' + fn);
  os.system('/hosted/opt/public/icm/perl/icm/sync_grep.pl -f ' + fn);

  # iii   Backup the new file from the depot - pre-merge.
  try:
    os.system('chmod +w ' + fn + '.orig');
    os.system('chmod +w ' + rf);
    shutil.move(fn + '.orig', rf)
  except:
    print "Couldn't move the Depot file to backup area"
  
  # iv.  diff two files 
  os.system('icmdiff3 {} {} -o {}'.format(bf, rf, fn))

  # v.   local edit it again 
  os.system('chmod +w ' + fn);

def restore_file(fn):
  (fn, ds, rf, com) = _search_local_edits(fn)
  print "WARN: Restoring " + fn 
  print "WARN: All local edits will be lost"
  confirm = raw_input("INFO: Do you want to continue [Y/y]");
  if(confirm.lower() == 'y'):
    print "INFO: Restored file: ",
    print fn
    shutil.copy(rf, fn)
    os.system('chmod -w ' + fn);
    display_list()
  
if __name__ == "__main__":  # Check for the right version of python
  if sys.version_info < (2, 7):
    raise "ERROR: Use python version 2.7 or greater"

  local_edits = _init_read()

  if(len(sys.argv) == 1):
    display_list()
    sys.exit(-1)

  # Init some stuff
  commandLine = argparse.ArgumentParser(description='Opens an ICM file for local edit.',
                                   usage='%(prog)s [options] [filename]')
  commandLine.add_argument('-d', '--diff',      help='Displays the difference from the original file', default=False, action='store_true')
  commandLine.add_argument('-r', '--restore',   help='Restore the file without local edits',           default=False, action='store_true')
  commandLine.add_argument('-s', '--sync',      help='Get latest and merge local changes',             default=False, action='store_true')
  commandLine.add_argument('-debug', '--debug', help='Display internal state',                         default=False, action='store_true')
  commandLine.add_argument('file_name',         help='ICM file_name to open or display diff of',       default="",  action='store')
  commandLine.add_argument('comment',           help='Add a comment why youre doing the local edit ',  default=None,  action='store', nargs='*')

  opt = commandLine.parse_args()

  if(opt.debug):
    print "\n(c) u-blox Ireland, Ltd."
    print "Backup area : " + local_edit_dir
    print "Pickle File : " + local_edit_list_fn + '\n'
    print "Debug information about currently locally edited files:"
    for (fn, ds, rf, com)in local_edits:
      print "File: {}\nDate: {}\nRestore: {}\nComment: {}\n\n".format(fn, ds, rf, com) 

    display_list()
  elif(opt.sync):
    sync_file(opt.file_name)
  elif(opt.diff):
    display_diff(opt.file_name)
  elif(opt.restore):
    restore_file(opt.file_name)
  else:
    add_new_file(os.path.abspath(sys.argv[1]), " ".join(sys.argv[2:]) )

