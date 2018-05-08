#!/usr/bin/python

import commands
import time
import sys
import os

issued = 3 
used   = 3

if len(sys.argv) == 2:
  libtype_name = sys.argv[1]
else:
  libtype_name = "rtlc"

lic_name = {}
lic_name["rtlc"] = "Genus_Synthesis"
lic_name["spyglass"] = "checker"

while used == issued:
  output = commands.getoutput("lmstat -a | grep " + lic_name[libtype_name])

  if len(output) == 0:
    print "lmstat command failed"
    sys.exit(-1)

  idx_issued = output.rindex(' licenses issued')
  idx_used   = output.rindex(' licenses in use')

  issued = output[idx_issued-1]
  used   = output[idx_used-1]
  print "{0} licenses: {1} available, {2} used".format(libtype_name, issued, used)
  if(used == issued):
    time.sleep(30)

os.system('notify-send -t 5000 "Synthesis license is now free"')
