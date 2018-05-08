#!/usr/bin/python

import argparse
import sys
import pickle
import os
import re
from tabulate import *

"""
TODO
====

- Parse the natural language due date
- Added estimated duration (maybe) +am/pm for morning/afternoon or +1 for a day etc.
- finish/delete a task
- list by tags
- Add work timesheet
- Export to nice webpage
- blocked by msg or task_id
- priority (maybe)

"""


#TODO : Do this properly
PATH_TO_TASKS_FILE = '/home/prya/.todo/todo.pkl'

class task_list:

  def __init__(self):
    self._list = []
    self.dirty = False

  def append(self, task_desc):
    new_task = task_item(task_desc)
    new_task.task_id = len(self._list) + 1
    self._list.append(new_task)
    self.dirty = True
  
  def __str__(self):
    hdr = ['Task ID', 'Description', 'Active', 'Blocked', 'Duration', 'Due']
    rows = []
    for task in self._list:
      rows.append(task.get())
    return tabulate(rows, headers=hdr)

  def __iter__(self):
    return self._list.__iter__()

class task_item:

  def __init__(self, desc):
    self.active   = False
    self.blocked  = False
    self.timesheet= []
    self.tags     = []
    self.due      = None
    self.desc     = desc
    self._parse_task()

  def _parse_date(self, date_str):
    date_str = date_str.to_lower()


  def _parse_task(self):
    # Create a string description
    self.desc = " ".join(self.desc) + '\n'

    #Get the tags, and remove from description
    self.tags = re.findall("#(.*?)[\s+]", self.desc)
    for tag in self.tags:
      self.desc = self.desc.replace('#'+tag, '')
    print self.tags

    # Get the time stamps and remove from description
    self._parse_date(re.findall("\@(.*?)[\s+]", self.desc))

  def log_time(self):
    pass

  def is_active(self):
    return self.active

  def is_blocked(self):
    return self.blocked

  def finish(self):
    pass

  def time(self):
    return "0h0m0s"

  def get(self):
    return [self.task_id, self.desc, self.active, self.blocked, self.time(), self.due]

def load_tasks():
  if(os.path.exists(PATH_TO_TASKS_FILE) == True):
    pfh = open(PATH_TO_TASKS_FILE, 'rb')
    tasks = pickle.load(pfh)
    pfh.close()
    return tasks
  else:
    return None


def save_tasks(tasks):
  pfh = open(PATH_TO_TASKS_FILE, 'wb')
  pickle.dump(tasks, pfh )
  pfh.close()

if __name__=="__main__":
  
  commandLine = argparse.ArgumentParser(description='Simple TODO list manager',
                                   usage='%(prog)s [args]')
  commandLine.add_argument('-l',           '--list', action='store_true', help='Lists all the outstanding tasks', default=False)
  commandLine.add_argument('taskname',           help='Add a new task to the list',  default=None,  action='store', nargs='*')

  """                                   
  commandLine.add_argument('-in',           '--inputs', action='store_true', help='List of inputs', default=False)
  commandLine.add_argument('-out',          '--outputs', action='store_true', help='List of outputs', default=False)
  commandLine.add_argument('-inst',         '--instances', action='store_true', help='List of instances', default=False)
  commandLine.add_argument('-inst_tree',    '--instance_tree', action='store_true', help='List of instances in a hierarchical tree format', default=False)
  commandLine.add_argument('-con',          '--connections', action='store_true', help='List of connections for an instance', default=False)
  commandLine.add_argument('-com',          '--compare', action='store_true', help='Compare the ports of 2 modules', default=False)
  commandLine.add_argument('-unld_in',      '--unloaded_inputs',    action='store_true', help='List the inputs that are unloaded internally', default=False)
  commandLine.add_argument('-undrv_out',    '--undriven_outputs', action='store_true', help='List the outputs that are undriven internally', default=False)
  commandLine.add_argument('-vhdl_pkg',     '--vhdl_package', action='store_true', help='Dumps out a VHDL package for a verilog module', default=False)
  commandLine.add_argument('-mt',           '--module_type')
  commandLine.add_argument('-mi',           '--module_inst')
  commandLine.add_argument('-sc',           '--strip_comments', action='store_true', help='Strips all the comments from the source files', default=False)
  commandLine.add_argument('-sn',           '--split_netlist', action='store_true', default=False, help='Split a single file netlist into a set of files in a new directory called netlist')
  commandLine.add_argument('file_list', help='List of verilog files', nargs='*')

  if(opt.compare):
    compare_modules(opt.file_list)
    sys.exit()
  """
  opt = commandLine.parse_args()
  
  tasks = load_tasks()
  if tasks == None:
    tasks = task_list()

  if(opt.list or (len(opt.taskname) == 0)):
    print tasks

  elif(opt.taskname != None):
    print "Adding task " + str.join(' ',  opt.taskname)
    tasks.append(opt.taskname)

  if(tasks.dirty):
    save_tasks(tasks)
