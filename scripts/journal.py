import glob
import fnmatch
import os

matches = []
for root, dirnames, filenames in os.walk('/home/prya/Desktop/filebackup/current/201703/'):
    for filename in fnmatch.filter(filenames, '*'):
        matches.append(os.path.join(root, filename))

print matches        
