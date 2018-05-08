import os
import sys

cwd = os.getcwd()

ws = cwd.split('/')[5]
print "Workspace: " + ws

blk = ws.split('+')[1][3:]
print "Blockname: " + blk

nwd = '/hosted/projects/prya/icm/' + ws + '/' + sys.argv[1] + '/' + blk
os.system('pushd ' + nwd)
