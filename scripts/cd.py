#!/usr/bin/python
import os
import sys
import pickle

try:
  workspace= os.environ['WORKSPACE']
except:
  print "Only works in a valid WORKSPACE"
  sys.exit(-1)

k_dir_stack_depth = 5

"""
When a file is opened in a directory that is part of a workspace, the director is
stored in a k_dir_stack_depth deep stack.
"""
def pushDirectoryToStack():
  
  # Read the current stack from file
  try:
    dir_stack = pickle.load( open(workspace + '/.directory_stack.pkl', 'rb') )
  except IOError:
    dir_stack = []

  # Add the new directory to the stack.
  rel_path = os.getcwd()[len(workspace)+1:]

  if rel_path in dir_stack:
    pass
  else:
    dir_stack.append(rel_path)
    if( len(dir_stack) > k_dir_stack_depth) :
      del dir_stack[0]
    pickle.dump(dir_stack, open(workspace + '/.directory_stack.pkl', 'wb') )
    
def popDirectoryToStack():
  try:
    dir_stack = pickle.load( open(workspace + '/.directory_stack.pkl', 'rb') )
  except IOError:
    sys.exit(0)

  print workspace + ':'
  for dir in dir_stack:
    print 'cd $WORKSPACE/' + dir

if __name__ == "__main__":

  if(len(sys.argv) > 1):
    pushDirectoryToStack()
  else:
    popDirectoryToStack()

