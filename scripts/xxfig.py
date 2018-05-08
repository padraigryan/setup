#!/usr/bin/python
################################################################################
#
#    Copyright 2012 Padraig Ryan
#    All Rights Reserved
#
#    Date: 23/04/2015
#
#    Use: Alias the xfig command to call this script and pass the paramereters
#    to it.  
#
#    Purpose:   To keep .fig in a single tidy directory
#
################################################################################

import sys
import os
import shutil

#k_xfig = '/usr/bin/xfig '
k_xfig = '/home/prya/usr/bin/xfig'
k_xfig_params = ' -metric -library_dir ~/usr/xfig -nosplash -specialtext -startfontsize 8 -startpsFont Helvetica  -startgridmode 1 -exportLanguage pdf $1'

# If set to true will export the .fig to the formats defined in fig2dev_params when xfig exits
k_auto_export = True

# Main script entry
if __name__ == "__main__":

  fig2dev_params = {}
  fig2dev_params['png'] = '-L png -m 5.0'
  fig2dev_params['pdf'] = '-L pdf'
  
  # Check if a file name was supplied
  try:
    file_dir = sys.argv[1]
  except:
    os.system(k_xfig + k_xfig_params)
    sys.exit()
    
  # Trim the trailing / if there is one
  if file_dir[-1:] == '/':
    file_dir = file_dir[:-1]

  # Add the .fig extention if there isn't one
  if file_dir[-4:] != '.fig':
    file_dir = file_dir + '.fig'

  # If the fig/directory hasn't been created yet, create it. i.e. new file
  if not os.path.exists(file_dir):
    os.makedirs(file_dir)

  # Create the command line
  file_name = file_dir + '/' + file_dir
  os.system(k_xfig + k_xfig_params + file_name)

  # Check if a file(s) was created, delete if the directory doesn't contain anything.
  if (not os.listdir(file_dir) ):
    shutil.rmtree(file_dir)
    sys.exit()

  # If enabled, export to all the formats listed.
  if(k_auto_export):
    for format in fig2dev_params:
      print 'Exporting : ' + format
      exp_file_name = file_name[:-3] + format
      os.system('fig2dev ' + fig2dev_params[format] + ' ' + file_name + ' ' + exp_file_name)

    print "To preview:"
    print 'gthumb ' + file_name[:-3] + 'png'
    print 'acroread ' + file_name[:-3] + 'pdf'
  
