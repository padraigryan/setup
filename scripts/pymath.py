import sys
from code import InteractiveConsole

import re

class FileCacher:
    "Cache the stdout text so we can analyze it before returning it"
    def __init__(self): self.reset()
    def reset(self): self.out = []
    def write(self,line): self.out.append(line)
    def flush(self):
        output = '\n'.join(self.out)
        self.reset()
        return output
#operators = ['=', '+', '-', '*', '/']
units = {'M':1000000, 'k':1000, 'm':0.001, 'u':0.000001}

def in_filter(line):
  operands = re.split("[=+\-*/]+", line)
  line = ""
  for operand in operands:
    for (key, val) in units.iteritems():
      operand = operand.replace(key, "*" + str(val))
    line = line + '(' + operand + ')'
  print line
  return line

class Shell(InteractiveConsole):
    "Wrapper around Python that can filter input/output to the shell"
    def __init__(self):
        self.stdout = sys.stdout
        self.cache = FileCacher()
        InteractiveConsole.__init__(self)
        return

    def get_output(self): sys.stdout = self.cache
    def return_output(self): sys.stdout = self.stdout

    def push(self,line):
        self.get_output()
        # you can filter input here by doing something like
        line = in_filter(line)
        InteractiveConsole.push(self,line)
        self.return_output()
        output = self.cache.flush()
        # you can filter the output here by doing something like
        # output = filter(output)
        print output # or do something else with it
        return 

if __name__ == '__main__':
  in_filter("2m+3u");
  asdf
  sh = Shell()
  sh.interact("Python Engineering Math")
