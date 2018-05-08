#!/usr/bin/python
################################################################################
#
#    Copyright 2014 Padraig Ryan
#    All Rights Reserved
#
#    Date: 4/12/2014
#
#    Use: Alias the gvim command to call this script and pass the paramereters
#    to it.
#
#    Purpose:   1) 
#
################################################################################
import sys
import re
import os
import glob
import sys
import fileinput

# Main script entry
if __name__ == "__main__":

  # Remove the script name
  argv = sys.argv[1:]

  # Remove the trailing carriage returns
  tmp_file_cnt = 1
  src_file_list = ""
  for file in argv:  
    tmp_file_name = "~/.tmp/tmp" + str(tmp_file_cnt)
    os.system("echo " + file + " > " + tmp_file_name)
    os.system("echo ##,## >> " + tmp_file_name)
    os.system("tr -d '\r' < " + file + " >> " + tmp_file_name)
    src_file_list = src_file_list + tmp_file_name + ' '
    tmp_file_cnt = tmp_file_cnt + 1
  
  # Combine the files
  os.system("paste -d',' "+src_file_list+"> ~/.tmp/plot_file.dat")

  os.system("java -jar /home/prya/usr/LiveGraph.2.0.beta01.Complete/LiveGraph.2.0.beta01.Complete.jar -f ~/.tmp/plot_file.dat")
