#!/bin/env python

import sys
import os
import argparse
import math
import string
import re
import time
import inspect
import subprocess
import datetime

# ------------------------------------------------------------------------------
#   _   _                      _                   _             
#  | | | | ___  _   _ ___  ___| | _____  ___ _ __ (_)_ __   __ _ 
#  | |_| |/ _ \| | | / __|/ _ \ |/ / _ \/ _ \ '_ \| | '_ \ / _` |
#  |  _  | (_) | |_| \__ \  __/   <  __/  __/ |_) | | | | | (_| |
#  |_| |_|\___/ \__,_|___/\___|_|\_\___|\___| .__/|_|_| |_|\__, |
#                                           |_|            |___/ 
# 
# ------------------------------------------------------------------------------
def check_if_logged_into_perforce():
   # None of this script works unless the user is logged into perforce, 
   # therefore this routine is used at the very start of the script to ensure
   # that the user is logged in.
   username = os.environ["USER"]
   print_status(1,"ubx_icm.py","subroutine start","check_if_logged_into_perforce")
   icmp4_command_to_check_login_status = "icmp4 login -s"
   print_status(2,"ubx_icm.py","command", icmp4_command_to_check_login_status)
   try:
      check_login_status = subprocess.check_output([icmp4_command_to_check_login_status], shell = True)
      print_status(1,"ubx_icm.py","info","User " + username  + " is logged in.")
   except subprocess.CalledProcessError as check_login_status_exception:
      print_status(1,"ubx_icm.py","info","User " + username  + " is not logged in.")
      print_status(1,"ubx_icm.py","info","Type: % icmp4 login")
      print_status(1,"ubx_icm.py","info","and give your UNIX password to login to perforce before using this script.")
      print_status(4,"ubx_icm.py","info","Quitting here.")
   print_status(1,"ubx_icm.py","subroutine end","check_if_logged_into_perforce")

# -----------------------------------------------------------------------------
def check_to_see_if_the_project_exists(project_name, subcommand):
   # If the project doesn't exist, then we need to quit the
   # script, because all other pm commands will fail.
   # This sub-routine checks the existence of the project. 
   print_status(1,"ubx_icm.py","subroutine start","check_to_see_if_the_project_exists")
   pm_command_to_check_existence_of_project = "pm project -l " + project_name
   print_status(2,"ubx_icm.py","command", pm_command_to_check_existence_of_project)

   # There are four scenarios:
   # - the project doesn't exist but we want to create it (that's OK).
   # - the project doesn't exist and we want to do something other than create it (that's not OK).
   # - the project exists and we still want to create it (that's not OK).
   # - the project exists and we don't want to create it (that's OK).
   try:
      check_login_status = subprocess.check_output([pm_command_to_check_existence_of_project], shell = True)
      print_status(1,"ubx_icm.py","info",project_name + " exists")
      if (subcommand == "cfp"):
         print_status(3,"ubx_icm.py","info","It already exists - so we shouldn't try to create it.")
         print_status(4,"ubx_icm.py","info","Quitting here.")
   except subprocess.CalledProcessError as check_login_status_exception:
      print_status(1,"ubx_icm.py","info",project_name + " does not exist")
      if (subcommand == "cfp"):
         print_status(3,"ubx_icm.py","info","OK - let's create it.")
      else:
         print_status(4,"ubx_icm.py","info","Quitting here.")
   print_status(1,"ubx_icm.py","subroutine end","check_to_see_if_the_project_exists")

# -----------------------------------------------------------------------------
def change_verbosity_value(verbosity):
   # This is purely a house-keeping routine. 
   # The default verbosity_value is 1 (verbosity low), which will show which routines are being entered and left.
   # verbosity_value 2 (verbosity medium) shows the subroutines and the commands being run.
   # verbosity_value 3 (verbosity high) shows the subroutines, the commands being run and any relevant information (e.g. loop indices).
   # verbosity_value 0 (verbosity off) shows nothing
   # verbosity_value 4 is an error
   # verbosity commands_only will only show commands 
   print_status(1,"ubx_icm.py","subroutine start","change_verbosity_value")
   if (verbosity == 'high'):
      verbosity_value  = 3
   if (verbosity == 'med'):
      verbosity_value  = 2
   if (verbosity == 'low'):
      verbosity_value  = 1
   if (verbosity == 'off'):
      verbosity_value  = 0
   if (verbosity == 'commands_only'):
      commands_only    = 1
   print_status(1,"ubx_icm.py","subroutine start","change_verbosity_value")

# -----------------------------------------------------------------------------
def print_status(level, program_name, message_type, status_string):
   # This is an important debugging and tracing routine
   # which allows the developer to see where the program is
   # failing during erroneous behaviour
   """ @@fore add note """
   if level == 0:
      level_string = 'INFO'
   if level == 1:
      level_string = 'LOW'
   if level == 2:
      level_string = 'MED'
   if level == 3:
      level_string = 'HIGH'
   if level == 4:
      level_string = 'ERROR'

   level_string = ''

   # Returns the current line number in our program.
   current_line = inspect.currentframe().f_back.f_lineno
   current_line_string = str(inspect.currentframe().f_back.f_lineno)
   if current_line < 100:
      current_line_string = " " + str(inspect.currentframe().f_back.f_lineno)
   if current_line < 10:
      current_line_string = "  " + str(inspect.currentframe().f_back.f_lineno)
   full_status_string = "[" + program_name + "]: " + current_line_string + " (" + '{0: <16}'.format(message_type) + ") " + status_string

   # this is a way to see the commands only
   # print "commands_only = " + str(commands_only)
   # print "level = " + str(level)
   if (commands_only == 1):
      if (level == 2): 
         print status_string
   else:
      if (level <= int(verbosity_value)):
         print full_status_string

   # for debug purposes
   if level == 4:
      sys.exit(1)

# -----------------------------------------------------------------------------
def date_in_yywwWW_format():
   # The tag is defined as <block>__<yy>ww<work_week_number>r<project_phase>_<four_digit_version_number>
   # e.g. uart__15ww42r1_0043
   # this indicates the block is "uart". 
   # This version was created in 2015, workweek 42. 
   # It's in project phase 1 and it's version 43.
   # This function generates the <yy>ww<work_week_number> string from the current time.
   today = datetime.date.today()
   yywwWW = today.strftime('%yww%W')
   print_status(3,"ubx_icm.py","info","The year/work week format is calculated as: " + yywwWW)
   return yywwWW

def find_library_types(project_name, project_variant):
   print_status(1,"ubx_icm.py","subroutine start","find_library_types")
   library_type_list = []
   pm_command_to_find_current_library_types = "pm variant -l " + project_name + " " + project_variant
   print_status(2,"ubx_icm.py","command", pm_command_to_find_current_library_types)
   try:
      current_library_types                     = subprocess.check_output([pm_command_to_find_current_library_types], shell=True)
      current_library_types_string              = current_library_types.decode("utf-8")
      current_library_types_string_lines        = current_library_types_string.splitlines()
      current_library_types_string_lines_length = len(current_library_types_string_lines)
      for j in range(0,current_library_types_string_lines_length):
         library_type = current_library_types_string_lines[j]
         library_type = re.sub(".*LibType=\"","", library_type)
         library_type = re.sub("\".*",        "", library_type)
         print_status(3,"ubx_icm.py","info","Found " + library_type)
         library_type_list.append(library_type)
      print_status(1,"ubx_icm.py","subroutine end","find_library_types")
      return library_type_list
   except subprocess.CalledProcessError as current_library_types_exception:
      print_status(3,"ubx_icm.py","info","No libraries found")
      return library_type_list

# ------------------------------------------------------------------------------
#   ___ ____ __  __   _____                 _   _                 
#  |_ _/ ___|  \/  | |  ___|   _ _ __   ___| |_(_) ___  _ __  ___ 
#   | | |   | |\/| | | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
#   | | |___| |  | | |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
#  |___\____|_|  |_| |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#                                                                 
# ------------------------------------------------------------------------------
def create_project(project_name):
   print_status(1,"ubx_icm.py","subroutine start","create_project")
   pm_command_create_project = "pm project -c IC_Design_Projects/playground/alternative " + project_name
   print_status(2,"ubx_icm.py","command", pm_command_create_project)
   subprocess.check_output([pm_command_create_project], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","create_project")

# ------------------------------------------------------------------------------
def remove_project(project_name):
   print_status(1,"ubx_icm.py","subroutine start","remove_project")
   pm_command_remove_project = "pm project -x " + project_name
   print_status(2,"ubx_icm.py","command", pm_command_remove_project)
   subprocess.check_output([pm_command_remove_project], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","remove_project")

# ------------------------------------------------------------------------------
def create_variant(project_name):
   print_status(1,"ubx_icm.py","subroutine start","create_variant")
   pm_command_create_variant = "pm variant " + project_name + " trunk"
   print_status(2,"ubx_icm.py","command", pm_command_create_variant)
   subprocess.check_output([pm_command_create_variant], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","create_variant")

# ------------------------------------------------------------------------------
def remove_variant(project_name):
   print_status(1,"ubx_icm.py","subroutine start","remove_variant")
   library_type_list = find_library_types(project_name, "trunk")
   for library_type in library_type_list:
      pm_command_remove_variant = "pm variant -x " + project_name + " " + library_type + " trunk"
      print_status(2,"ubx_icm.py","command", pm_command_remove_variant)
      subprocess.check_output([pm_command_remove_variant], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","remove_variant")

# ------------------------------------------------------------------------------
def create_library_type_list(project_name, library_type_list):
   print_status(1,"ubx_icm.py","subroutine start","create_library_type_list")
   for library_type in library_type_list:
      pm_command_create_library_type_list = "pm variant " + project_name + " " + library_type + " trunk"
      print_status(2,"ubx_icm.py","command", pm_command_create_library_type_list)
      subprocess.check_output([pm_command_create_library_type_list], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","create_library_type_list")

# ------------------------------------------------------------------------------
def create_libraries(project_name, library_type_list):
   print_status(1,"ubx_icm.py","subroutine start","create_libraries")
   library_name = project_name.replace("ic_","")
   for library_type in library_type_list:
      pm_command_create_libraries = "pm library -p " + project_name + " trunk " + library_type + " " + library_name
      print_status(2,"ubx_icm.py","command", pm_command_create_libraries)
      subprocess.check_output([pm_command_create_libraries], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","create_libraries")

def remove_libraries(project_name):
   print_status(1,"ubx_icm.py","subroutine start","remove_libraries")
   library_type_list = find_library_types(project_name, "trunk")
   library_name = project_name.replace("ic_","")
   for library_type in library_type_list:
      pm_command_remove_libraries = "pm library -xgpsms1 -F -p " + project_name + " trunk " + library_type + " " + library_name
      print_status(2,"ubx_icm.py","command", pm_command_remove_libraries)
      subprocess.check_output([pm_command_remove_libraries], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","remove_libraries")

# ------------------------------------------------------------------------------
def clone_library_activedev_configurations(project_name,  library_type_list, incremented_configuration):
   print_status(1,"ubx_icm.py","subroutine start","clone_library_activedev_configurations")
   library_name = project_name.replace("ic_","")
   for library_type in library_type_list:
      # Clone the ActiveDev library type configuration into the new "incremented_configuration"
      pm_command_clone_library_activedev_configuration = "pm configuration -n " + incremented_configuration + " " + project_name + " trunk ActiveDev -t " + library_type
      print_status(2,"ubx_icm.py","command", pm_command_clone_library_activedev_configuration)
      subprocess.check_output([pm_command_clone_library_activedev_configuration], shell=True)
      # and now hook it to the correct release (as opposed to ActiveDev
      library_name_at_incremented_configuration = library_name + "@" + incremented_configuration
      pm_command_hook_library_configuration_to_correct_release = "pm configuration -f -t " + library_type + " " + project_name + " trunk " + incremented_configuration + " " + library_name_at_incremented_configuration
      print_status(2,"ubx_icm.py","command", pm_command_hook_library_configuration_to_correct_release)
      subprocess.check_output([pm_command_hook_library_configuration_to_correct_release], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","clone_library_activedev_configurations")

def create_library_configurations(project_name, library_type_list, configuration_name):
   print_status(1,"ubx_icm.py","subroutine start","create_library_configurations")
   library_name = project_name.replace("ic_","")
   for library_type in library_type_list:
      pm_command_create_library_configuration = "pm configuration -t " + library_type + " " + project_name + " trunk " + configuration_name + " " + library_name
      print_status(2,"ubx_icm.py","command", pm_command_create_library_configuration)
      subprocess.check_output([pm_command_create_library_configuration], shell=True)
   print_status(1,"ubx_icm.py","subroutine end","create_library_configurations")

def remove_library_configurations(project_name):
   print_status(1,"ubx_icm.py","subroutine start","remove_library_configurations")
   library_type_list = find_library_types(project_name, "trunk")
   for library_type in library_type_list:
      pm_command_to_find_library_configurations = "pm configuration -l " + project_name + " trunk -t " + library_type
      print_status(2,"ubx_icm.py","command", pm_command_to_find_library_configurations)
      try:
         library_configurations                     = subprocess.check_output([pm_command_to_find_library_configurations], shell = True)
         library_configurations_string              = library_configurations.decode("utf-8")
         library_configurations_string_lines        = library_configurations_string.splitlines()
         library_configurations_string_lines_length = len(library_configurations_string_lines)
         for j in range(0,library_configurations_string_lines_length):
            library_configuration = library_configurations_string_lines[j]
            library_configuration = re.sub(".*Configuration=\"","",library_configuration)
            library_configuration = re.sub("\".*","",library_configuration)
            print_status(2,"ubx_icm.py","command","pm configuration -xgpsms1 -t " + library_type + " " + project_name + " trunk " + library_configuration)
            subprocess.call(["pm", "configuration", "-xgpsms1", "-t", library_type, project_name, "trunk", library_configuration])
      except subprocess.CalledProcessError as library_configurations_exception:
         print_status(1,"ubx_icm.py","info","no library configurations")
   print_status(1,"ubx_icm.py","subroutine end","remove_library_configurations")

# ------------------------------------------------------------------------------
#    ____                                          _   _     _            
#   / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| | | |   (_)_ __   ___ 
#  | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` | | |   | | '_ \ / _ \
#  | |__| (_) | | | | | | | | | | | (_| | | | | (_| | | |___| | | | |  __/
#   \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_| |_____|_|_| |_|\___|
#                                                                         
#   ____                          
#  |  _ \ __ _ _ __ ___  ___ _ __ 
#  | |_) / _` | '__/ __|/ _ \ '__|
#  |  __/ (_| | |  \__ \  __/ |   
#  |_|   \__,_|_|  |___/\___|_|   
# 
# ------------------------------------------------------------------------------
def parseCommandLine():
   """ Function to parse the command line arguments """
   print_status(0,"ubx_icm.py","info","Parsing the command line")
   commandLine = argparse.ArgumentParser(prog='PROG', description=' A foo that bars', usage='%(prog)s FILL_IN_HERE  try: %(prog)s --help'                                                                                                     )
   commandLine.add_argument('subcommand',                 choices=['cp', 'cv', 'ct', 'cl', 'clc', 'ccc', 'rp', 'rv', 'rt', 'rl', 'rlc', 'rcc', 'cfp', 'rfp', 'lc', 'nc', 'ngr'], help='This is the subcommand (required).'                    )
   commandLine.add_argument('project_name',                                                                                                                                      help='This is the name of the project (required).'           )
   commandLine.add_argument('--project_type',             choices=['rtl','verif','tb', 'all'],                                                                                   help='This is the project type (required).'                  )
   commandLine.add_argument('--library_type_list',        choices=['tb','rtl','uvm'],                                                                                            help='This is optional',                            nargs='*')
   commandLine.add_argument('--verbosity',                choices=['off','low','med','high','commands_only'],                                                                    help='This is optional'                                      )
   commandLine.add_argument('--increment_project_phase',  choices=['yes','no'],                                                                                                  help='This is optional'                                      )
   command_line_arguments = commandLine.parse_args()
   print_status(0,"ubx_icm.py","info","Command line is parsed")
   return command_line_arguments

# ------------------------------------------------------------------------------
#    ____ _       _           _ 
#   / ___| | ___ | |__   __ _| |
#  | |  _| |/ _ \| '_ \ / _` | |
#  | |_| | | (_) | |_) | (_| | |
#   \____|_|\___/|_.__/ \__,_|_|
# 
#   ____      _                     
#  |  _ \ ___| | ___  __ _ ___  ___ 
#  | |_) / _ \ |/ _ \/ _` / __|/ _ \
#  |  _ <  __/ |  __/ (_| \__ \  __/
#  |_| \_\___|_|\___|\__,_|___/\___|
# 
# ------------------------------------------------------------------------------

def create_global_release(project_name, increment_project_phase):
   print_status(1,"ubx_icm.py","subroutine start","create_global_release")
   
   # PYTHON: The following line runs a shell command and sends the byte array result of that command to the pm_output variable
   # ICM: finds a list of all the libraries and library types in the project.
   pm_command_to_list_all_libraries_in_project = 'pm library -l -p ' + project_name + ' trunk'
   print_status(2,"ubx_icm.py","command", pm_command_to_list_all_libraries_in_project)

   # PYTHON: get the result of the command into a variable called pm_output
   all_libraries_in_project = subprocess.check_output([pm_command_to_list_all_libraries_in_project], shell=True)

   # PYTHON: The following line converts a byte array to a string
   all_libraries_in_project_string = all_libraries_in_project.decode("utf-8")

   # PYTHON: The following line splits the string based on the new lines.
   all_libraries_in_project_string_lines = all_libraries_in_project_string.splitlines()

   # We don't know what library types are in the project, so this routine gets an array
   all_libraries_in_project_string_lines_length = len(all_libraries_in_project_string_lines)
   max_change_number                               = 0
   for i in range(0,all_libraries_in_project_string_lines_length):
      library_name =  all_libraries_in_project_string_lines[i]
      library_name = re.sub(".*Library=\"","",library_name)
      library_name = re.sub("\".*","",library_name)
      print_status(3,"ubx_icm.py","info","library_name = " + library_name)
      
      library_type = all_libraries_in_project_string_lines[i]
      library_type = re.sub(".*LibType=\"","",library_type)
      library_type = re.sub("\".*","",library_type)

      pm_command_to_find_change_numbers               = "pm release -l -p " + project_name + " trunk " + library_type + " " + library_name + " -c"
      print_status(2,"ubx_icm.py","command", pm_command_to_find_change_numbers)
      change_numbers_of_libraries                     = subprocess.check_output([pm_command_to_find_change_numbers], shell = True)
      change_numbers_of_libraries_string              = change_numbers_of_libraries.decode("utf-8")
      change_numbers_of_libraries_string_lines        = change_numbers_of_libraries_string.splitlines()
      change_numbers_of_libraries_string_lines_length = len(change_numbers_of_libraries_string_lines)
      for j in range(0,change_numbers_of_libraries_string_lines_length):
         change_number = change_numbers_of_libraries_string_lines[j]
         change_number = re.sub(".*Change=\"","",change_number)
         change_number = re.sub("\".*","",change_number)
         print_status(3,"ubx_icm.py","info","change_number = " + str(change_number))
         print_status(3,"ubx_icm.py","info","max_change_number = " + str(max_change_number))
         if (int(change_number) > int(max_change_number)):
            max_change_number = int(change_number)
   print_status(3,"ubx_icm.py","info","final max_change_number = " + str(max_change_number))

   most_recent_configuration = get_current_configuration(project_name)
   incremented_configuration = increment_current_configuration(project_name, most_recent_configuration, increment_project_phase)

   for i in range(0,all_libraries_in_project_string_lines_length):
      library_name =  all_libraries_in_project_string_lines[i]
      library_name = re.sub(".*Library=\"","",library_name)
      library_name = re.sub("\".*","",library_name)
      print_status(3,"ubx_icm.py","info","library_name = " + library_name)
      
      library_type = all_libraries_in_project_string_lines[i]
      library_type = re.sub(".*LibType=\"","",library_type)
      library_type = re.sub("\".*","",library_type)
      print_status(3,"ubx_icm.py","info","library_type = " + library_type)

      # Need to get name of previous release and increment it once.
      # pm_command_to_create_a_global_release = "pm release -g -p " + project_name + " trunk " + library_type + " " + library_name + " " + str(max_change_number) + " " + incremented_configuration
      pm_command_to_create_a_global_release = "pm release -g -p " + project_name + " trunk " + library_type + " " + library_name + " latest " + incremented_configuration
      print_status(4,"ubx_icm.py","command", pm_command_to_create_a_global_release)

      global_release = subprocess.check_output([pm_command_to_create_a_global_release], shell = True)

   clone_library_activedev_configurations(project_name,  library_type_list, incremented_configuration)
   clone_composite_activedev_configuration(project_name, library_type_list, incremented_configuration)

   # create_library_configurations(project_name,  library_type_list, incremented_configuration)
   # create_composite_configuration(project_name, library_type_list, incremented_configuration)
   print_status(1,"ubx_icm.py","subroutine end","create_global_release")

# ------------------------------------------------------------------------------
#   __  __             _             _       _   _             
#  |  \/  | __ _ _ __ (_)_ __  _   _| | __ _| |_(_)_ __   __ _ 
#  | |\/| |/ _` | '_ \| | '_ \| | | | |/ _` | __| | '_ \ / _` |
#  | |  | | (_| | | | | | |_) | |_| | | (_| | |_| | | | | (_| |
#  |_|  |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|_| |_|\__, |
#                       |_|                              |___/
#    ____             __ _                       _   _                 
#   / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __  ___ 
#  | |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \/ __|
#  | |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | \__ \
#   \____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|___/
#                          |___/
# 
# ------------------------------------------------------------------------------
def create_composite_configuration(project_name, library_type_list, configuration_name):
   print_status(1,"ubx_icm.py","subroutine start","create_composite_configuration")
   length_of_library_type_list = len(library_type_list)
   configuration_name_at_library_type = configuration_name + "@" + library_type_list[0]
   subprocess.call(["pm", "configuration",       project_name, "trunk", configuration_name, configuration_name_at_library_type])
   for i in range(1,length_of_library_type_list):
      library_type = library_type_list[i]
      configuration_name_at_library_type = configuration_name + "@" + library_type
      pm_command_create_composite_configuration = "pm configuration -f " + project_name + " trunk " + configuration_name + " " + configuration_name_at_library_type
      print_status(2,"ubx_icm.py","command", pm_command_create_composite_configuration)
      subprocess.check_output([pm_command_create_composite_configuration], shell = True)
   print_status(1,"ubx_icm.py","subroutine end","create_composite_configuration")

def clone_composite_activedev_configuration(project_name, library_type_list, incremented_configuration):
   print_status(1,"ubx_icm.py","subroutine start","create_composite_configuration")

   # 1. Clone the ActiveDev composite configuration
   pm_command_clone_composite_activedev_configuration = "pm configuration -n " + incremented_configuration + " " + project_name + " trunk ActiveDev"
   print_status(2,"ubx_icm.py","command", pm_command_clone_composite_activedev_configuration)
   subprocess.check_output([pm_command_clone_composite_activedev_configuration], shell = True)

   length_of_library_type_list = len(library_type_list)
   for i in range(0,length_of_library_type_list):
      library_type = library_type_list[i]
      activedev_at_library_type_hash_none = "ActiveDev@" + library_type + "#none"
      # 2. Foreach library type remove ActiveDev library 
      #    configuration references from the new composite configuration
      pm_command_remove_library_activedev_configuration_from_composite_configuration = "pm configuration -f " + project_name + " trunk " + incremented_configuration + " "  + activedev_at_library_type_hash_none
      print_status(2,"ubx_icm.py","command", pm_command_remove_library_activedev_configuration_from_composite_configuration)
      subprocess.check_output([pm_command_remove_library_activedev_configuration_from_composite_configuration], shell = True)
      configuration_name_at_library_type = incremented_configuration + "@" + library_type
      # 3. Foreach library type add new library_type configuration to 
      #    the new composite configuration
      pm_command_add_new_library_configuration_to_new_composite_configuration = "pm configuration -f " + project_name + " trunk " + incremented_configuration + " " + configuration_name_at_library_type
      print_status(2,"ubx_icm.py","command", pm_command_add_new_library_configuration_to_new_composite_configuration)
      subprocess.check_output([pm_command_add_new_library_configuration_to_new_composite_configuration], shell = True)
   print_status(1,"ubx_icm.py","subroutine end","create_composite_configuration")


def remove_composite_configuration(project_name):
   print_status(1,"ubx_icm.py","subroutine start","remove_composite_configuration")
   pm_command_to_find_composite_configurations = "pm configuration -l " + project_name + " trunk "
   print_status(2,"ubx_icm.py","command", pm_command_to_find_composite_configurations)
   try:
      composite_configurations                     = subprocess.check_output([pm_command_to_find_composite_configurations], shell = True)
      composite_configurations_string              = composite_configurations.decode("utf-8")
      composite_configurations_string_lines        = composite_configurations_string.splitlines()
      composite_configurations_string_lines_length = len(composite_configurations_string_lines)
      for j in range(0,composite_configurations_string_lines_length):
         composite_configuration = composite_configurations_string_lines[j]
         composite_configuration = re.sub(".*Configuration=\"","",composite_configuration)
         composite_configuration = re.sub("\".*","",composite_configuration)
         pm_command_remove_composite_configuration = "pm configuration -xgpsms1 " + project_name + " trunk " + composite_configuration
         print_status(2,"ubx_icm.py","command", pm_command_remove_composite_configuration)
         subprocess.check_output([pm_command_remove_composite_configuration], shell = True)
   except subprocess.CalledProcessError as composite_configurations_exception:
      print_status(1,"ubx_icm.py","info","no composite configurations")
   print_status(1,"ubx_icm.py","subroutine end","remove_composite_configuration")

def list_configurations(project_name):
   print_status(1,"ubx_icm.py","subroutine start","list_configurations")
   pm_command_list_configurations = "pm configuration -l " + project_name + " trunk -n ActiveDev"
   print_status(2,"ubx_icm.py","command", pm_command_list_configurations)
   subprocess.check_output([pm_command_list_configurations], shell = True)
   print_status(1,"ubx_icm.py","subroutine end","list_configurations")


def new_composite_configuration(project_name, library_type_list):
   print_status(1,"ubx_icm.py","subroutine start","new_composite_configuration")
   subprocess.call(['pm', 'configuration', '-l', project_name, 'trunk', '-n', "ActiveDev"])
   print_status(1,"ubx_icm.py","subroutine end","new_composite_configuration")

# ------------------------------------------------------------------------------
def get_current_configuration(project_name):
   library_name = project_name.replace("ic_","")
   print_status(1,"ubx_icm.py","subroutine start","get_current_configuration")
   pm_command_to_get_current_configuration    = "pm configuration -l " + project_name + " trunk"
   print_status(2,"ubx_icm.py","command", pm_command_to_get_current_configuration)
   list_of_configurations                     = subprocess.check_output([pm_command_to_get_current_configuration], shell = True)
   list_of_configurations_string              = list_of_configurations.decode("utf-8")
   list_of_configurations_string_lines        = list_of_configurations_string.splitlines()
   list_of_configurations_string_lines_length = len(list_of_configurations_string_lines)
   list_of_configurations_array = []
   for i in range(0,list_of_configurations_string_lines_length):
      configuration_name = list_of_configurations_string_lines[i]
      configuration_name = re.sub(".*Configuration=\"","",configuration_name)
      configuration_name = re.sub("\".*","",configuration_name)
      print_status(3,"ubx_icm.py","info","found configuration: " + configuration_name)
      list_of_configurations_array.append(configuration_name)
   list_of_configurations_array.remove('ActiveDev')
   list_of_configurations_array_length = len(list_of_configurations_array)
   print_status(3,"ubx_icm.py","info","The number of configurations found is: " + str(list_of_configurations_array_length))
   list_of_configurations_sorted = sorted(list_of_configurations_array, reverse=True)
   
   if (list_of_configurations_array_length < 1):
      most_recent_configuration = library_name + "__" + date_in_yywwWW_format() + "r0_0000"
   else:
      most_recent_configuration = list_of_configurations_sorted[0]
   print_status(3,"ubx_icm.py","info","most recent configuration = " + most_recent_configuration)
   print_status(1,"ubx_icm.py","subroutine end","get_current_configuration")
   return most_recent_configuration

def increment_current_configuration(project_name, existing_configuration, increment_project_phase):
   library_name = project_name.replace("ic_","")
   print_status(1,"ubx_icm.py","subroutine start","increment_current_configuration")
   project_stage = existing_configuration
   print_status(3,"ubx_icm.py","info","Existing configuration = " + existing_configuration)
   project_stage = re.sub("^.*__","",project_stage);
   project_stage = re.sub("^.*r","",project_stage);
   project_stage = re.sub("_.*","",project_stage);
   print_status(3,"ubx_icm.py","info","Found project stage: " + project_stage)
   if (increment_project_phase == 'yes'):
      project_stage = str(int(project_stage) + 1)
   print_status(3,"ubx_icm.py","info","New project stage = " + project_stage)

   project_revision = existing_configuration
   project_revision = re.sub(".*_","",project_revision);
   print_status(3,"ubx_icm.py","info","current project revision = " + project_revision)

   new_project_revision = int(project_revision) + 1

   if new_project_revision < 1000:
      new_project_revision_string = '0' + str(new_project_revision)
   if new_project_revision < 100:
      new_project_revision_string = '00' + str(new_project_revision)
   if new_project_revision < 10:
      new_project_revision_string = '000' + str(new_project_revision)
   print_status(3,"ubx_icm.py","info","new project revision = " + new_project_revision_string)

   new_configuration = library_name + "__" + str(date_in_yywwWW_format()) + "r" + project_stage + "_" + new_project_revision_string
   print_status(3,"ubx_icm.py","info","New configuration = " + new_configuration)

   print_status(1,"ubx_icm.py","subroutine end","increment_current_configuration")
   return new_configuration

def get_list_composite_configurations(project_name):
   print_status(1,"ubx_icm.py","subroutine start"," get_list_composite_configurations")
   pm_command_to_get_current_configuration    = "pm configuration -l " + project_name + " trunk"
   print_status(2,"ubx_icm.py","info","command " + pm_command_to_get_current_configuration)
   list_of_configurations                     = subprocess.check_output([pm_command_to_get_current_configuration], shell = True)
   list_of_configurations_string              = list_of_configurations.decode("utf-8")
   list_of_configurations_string_lines        = list_of_configurations_string.splitlines()
   list_of_configurations_string_lines_length = len(list_of_configurations_string_lines)
   list_of_configurations_array = []
   for i in range(0,list_of_configurations_string_lines_length):
      configuration_name = list_of_configurations_string_lines[i]
      configuration_name = re.sub(".*Configuration=\"","",configuration_name)
      configuration_name = re.sub("\".*","",configuration_name)
      list_of_configurations_array.append(configuration_name)
   print_status(1,"ubx_icm.py","subroutine end"," get_list_composite_configurations")
   return list_of_configurations_array

def get_list_library_configurations(project_name,library_name):
   print_status(1,"ubx_icm.py","subroutine start","get_list_library_configurations")
   pm_command_to_get_current_configuration    = "pm configuration -l " + project_name + " trunk " + library_name
   print_status(4,"ubx_icm.py","command", pm_command_to_get_current_configuration)
   
   list_of_configurations                     = subprocess.check_output([pm_command_to_get_current_configuration], shell = True)
   list_of_configurations_string              = list_of_configurations.decode("utf-8")
   list_of_configurations_string_lines        = list_of_configurations_string.splitlines()
   list_of_configurations_string_lines_length = len(list_of_configurations_string_lines)
   list_of_configurations_array = []
   for i in range(0,list_of_configurations_string_lines_length):
      configuration_name = list_of_configurations_string_lines[i]
      configuration_name = re.sub(".*Configuration=\"","",configuration_name)
      configuration_name = re.sub("\".*","",configuration_name)
      list_of_configurations_array.append(configuration_name)
   print_status(1,"ubx_icm.py","subroutine end","get_list_library_configurations")
   return list_of_configurations_array

# ------------------------------------------------------------------------------
#   __  __       _       
#  |  \/  | __ _(_)_ __  
#  | |\/| |/ _` | | '_ \ 
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#                        
# ------------------------------------------------------------------------------
if __name__ == "__main__":

   # set up verbosity
   global verbosity_value
   global commands_only
   verbosity_value = 1 
   commands_only   = 0

   # get the variables from the command line arguments
   command_line_arguments  = parseCommandLine()
   project_name            = command_line_arguments.project_name
   project_type            = command_line_arguments.project_type
   subcommand              = command_line_arguments.subcommand

   # adding some robustness to the script:
   # 1. make sure that the user is logged into perforce
   check_if_logged_into_perforce()

   # adding some robustness to the script:
   # 2. make sure that the project specified on the command line exists
   check_to_see_if_the_project_exists(project_name, subcommand)

   # Switch to increment the project phase
   # The project phase can be phase 0, phase 1 or phase 2.
   if (command_line_arguments.increment_project_phase == 'yes'):
      increment_project_phase = 'yes'
   else:
      increment_project_phase = 'no'
   
   # If the verbosity is set at the command line, this
   # section (and subroutine) will change the verbosity_value
   # The verbosity_value is used by the print_status subroutine
   # in order to print the appropriate messages to the screen.
   if command_line_arguments.verbosity:
      verbosity = command_line_arguments.verbosity
      if (verbosity == 'high'):
         verbosity_value  = 3
      if (verbosity == 'med'):
         verbosity_value  = 2
      if (verbosity == 'low'):
         verbosity_value  = 1
      if (verbosity == 'off'):
         verbosity_value  = 0
      if (verbosity == 'commands_only'):
         commands_only    = 1

   # Depending on the project type, the library types needed will be different
   if (project_type == "rtl"):
      library_type_list = ["rtl", "meta"]
   
   if (project_type == "tb"):
      library_type_list  = ["tb", "ncsim", "meta", "scripts", "uvm"]
   
   if (project_type == "verif"):
      library_type_list = ["uvm", "meta"]
   
   if (project_type == "all"):
      library_type_list = ["behaviour", "constraints", "doc", "meta", "ncsim", "rtl", "rtlc", "scripts", "tb", "spyglass"]

   # cp: create project
   if (subcommand == 'cp'):
      create_project(project_name)
   
   # rp: remove project
   if (subcommand == 'rp'):
      remove_project(project_name)
   
   # cv: create variant
   if (subcommand == 'cv'):
      create_variant(project_name)
   
   # rv: remove variant
   if (subcommand == 'rv'):
      remove_variant(project_name)
   
   # clt: create library types
   if (subcommand == 'ct'):
      create_library_type_list(project_name, library_type_list)
   
   # cl: create libraries 
   if (subcommand == 'cl'):
      create_libraries(project_name, library_type_list)
   
   # rl: remove libraries 
   if (subcommand == 'rl'):
      remove_libraries(project_name)
   
   # clc: create library configurations 
   if (subcommand == 'clc'):
      create_library_configurations(project_name, library_type_list, 'ActiveDev')
   
   # rlc: remove library configurations 
   if (subcommand == 'rlc'):
      remove_library_configurations(project_name)
   
   # ccc: create composite configuration  
   if (subcommand == 'ccc'):
      create_composite_configuration(project_name, library_type_list, 'ActiveDev')
   
   # rcc: remove composite configuration  
   if (subcommand == 'rcc'):
      remove_composite_configuration(project_name)
   
   # cfp: create full project
   if (subcommand == 'cfp'):
      print_status(1,"ubx_icm.py","subroutine call","create_project")
      create_project(project_name)
      print_status(1,"ubx_icm.py","subroutine call","create_variant")
      create_variant(project_name)
      print_status(1,"ubx_icm.py","subroutine call","create_library_type_list")
      create_library_type_list(project_name, library_type_list)
      print_status(1,"ubx_icm.py","subroutine call","create_libraries")
      create_libraries(project_name, library_type_list)
      print_status(1,"ubx_icm.py","subroutine call","create_library_configurations")
      create_library_configurations(project_name, library_type_list, 'ActiveDev')
      print_status(1,"ubx_icm.py","subroutine call","create_composite_configuration")
      create_composite_configuration(project_name, library_type_list, 'ActiveDev')
   
   # rfp: remove full project
   if (subcommand == 'rfp'):
      print_status(1,"ubx_icm.py","subroutine call","remove_composite_configuration")
      remove_composite_configuration(project_name)
      print_status(1,"ubx_icm.py","subroutine call","remove_library_configurations")
      remove_library_configurations(project_name)
      print_status(1,"ubx_icm.py","subroutine call","remove_libraries")
      remove_libraries(project_name)
      print_status(1,"ubx_icm.py","subroutine call","remove_variant")
      remove_variant(project_name)
      print_status(1,"ubx_icm.py","subroutine call","remove_project")
      remove_project(project_name)
   
   # lc: list configurations
   if (subcommand == 'lc'):
      list_configurations(project_name)
   
   # nc: new configuration
   if (subcommand == 'nc'):
      new_composite_configuration(project_name, library_type_list)
   
   # ngr: new global release
   if (subcommand == 'ngr'):
      create_global_release(project_name, increment_project_phase)
