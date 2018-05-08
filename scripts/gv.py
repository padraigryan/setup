#!/usr/bin/python
################################################################################
#
#    Copyright 2012 Padraig Ryan
#    All Rights Reserved
#
#    Date: 22/06/2012
#
#    Use: Alias the gvim command to call this script and pass the paramereters
#    to it.  
#
#    Purpose:   1) Opens gvim to certain line number by appending :<line Number>
#               2) Given a partial file name tries to find the intended file
#								3) Creates a backup file.
#
################################################################################

import sys
import re
import os
import glob
import sys
import pickle 

"""
Smarter opening of files including
- glob of partial file/path names and offer alternatives if more than one match
- jump to line number if there's a number at the end of the file name
- creates a backup of the file if it's not too big

TODO:
1) Create a backup opening and closing the file -  if they're the same then only one backup.
2) Auto zip the current directory if month has rolled over.



"""
k_enable_backup = True
k_backupdir = '/home/prya/Desktop/filebackup/current/'
k_max_backup_size = 10e+6

def SearchPartailPath(pathSearchTerm):

  folder_list = []

  #check for a path or just a partial file name
  if(re.search(r'/', pathSearchTerm) != None):
    m1 = ""
    m2 = ""
    m = re.sub(r'/', r'*/*', pathSearchTerm);
    m1 = re.sub(r'\.\.\*', '..', m)                                             # Don't want to mess with rel paths
    m2 = re.sub(r'\*\.\.', '..', m1)                                            # Don't want to mess with rel paths
    m2 = m2 + '*'
  else:
    m2 = '*' + pathSearchTerm + '*'

  folder_list = glob.glob(m2)

  return folder_list

#Check for partial filenames - pseudo file name completion 
def SearchForPartialFileName(fileToRead):

  if(os.path.exists(fileToRead) == True):
    return fileToRead

  else:
    potentialFiles = SearchPartailPath(fileToRead)

    if(len(potentialFiles) == 0):                                               # No matches - create new file
      return fileToRead

    elif(len(potentialFiles) == 1):      
      fileName = potentialFiles[0]

    else:                                                                       # Multiple matches, list and let user select
      choice = 1
      for fileNameEntry in potentialFiles:
        print str(choice) + ') ' + fileNameEntry
        choice = choice + 1
      
      try:
        getFileSelection = int(raw_input("Choose wisely: "))
      except ValueError:
        return None
      except KeyboardInterrupt:
        print '\n'
        return None
      
      if(getFileSelection >= choice):
        print "You sir, are an idiot!"
        return None

      else:
        fileName = potentialFiles[getFileSelection - 1]

  return fileName

def CheckGvimParameters(parameters):
  separation_chars = "[,:]"
  
  # No parameters defined, open a blank doc
  if(len(parameters) == 1):
      os.system('/home/prya/usr/bin/gvim')
      sys.exit(0)

  results = re.split(separation_chars, parameters[1]);

  cmdToExec = '' 

  # Format: gvim <fileName><char><space><lineNum>
  if(len(parameters) > 2):          
    potentialFilePath = results[0];
    jumpToLine = parameters[-1]
  # Format: gvim <fileName><char><lineNum>
  elif(len(results) >= 2): 
    potentialFilePath = results[0];
    jumpToLine = results[1]
  else:
    potentialFilePath = parameters[1];                                          # Best guess otherwise
    jumpToLine = "0"

  return (potentialFilePath, jumpToLine)

def createBackup(newBackupFile):
  """
  If the file is too big, don't back it up
  Creates a date/time stamped directory structure in the backup location 
  Copies the file to the new backup location 
  Saves the original location that it was copied from.
  """
  import datetime
  import shutil

  if(k_enable_backup == False):
    return
  
  # check if we're creating the file, if so, no point in backing it up
  if not os.path.isfile(newBackupFile):
    return

  # Check if it's really big, then don't backup it up
  if(os.stat(newBackupFile).st_size > k_max_backup_size):
    return

  datestamp = '%s/' % (datetime.datetime.now().strftime('%Y%m/%d%H%M%S'))
  backupPath = k_backupdir + datestamp 

  if not os.path.exists(backupPath):
    os.makedirs(backupPath)
    shutil.copyfile(newBackupFile, backupPath + os.path.basename(newBackupFile))
    fh = open(backupPath + '/location', 'w')
    print >>fh, os.path.abspath(newBackupFile)
    fh.close()

# Main script entry
if __name__ == "__main__":

  (potentialFilePath, jumpToLine) = CheckGvimParameters(sys.argv)

  fileName = SearchForPartialFileName(potentialFilePath)

  if(fileName == None):                                                         # Couldn't find a suitable candidate to open
    sys.exit(0);
  else:
    #cmdToExec = 'gvim ' + fileName + ' +' + jumpToLine + ' &>/dev/null'
    cmdToExec = '/home/prya/usr/bin/gvim ' + fileName + ' +' + jumpToLine 
    createBackup(fileName)
    os.system(cmdToExec)
