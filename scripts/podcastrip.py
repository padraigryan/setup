#!/home/prya/usr/bin/python

import urllib2
import datetime 
import os
import re

# Create new folder

dir_name = "/home/prya/Podcasts/" + str(datetime.date.today());

print dir_name

html = ""

try:
  os.stat(dir_name)
  f = open(dir_name + "/index.html", "r")
  html = f.read()

except:
  print "Getting the webpage"
  os.mkdir(dir_name)
  webpage = urllib2.urlopen('http://www.thisamericanlife.org');

  html = webpage.read()
  f = open(dir_name + "/index.html", "w")
  f.write(html)
  

start_tag = '<li class="download"><a href="'
end_tag   = '" download="'

s = re.search(start_tag+'(.+?)'+end_tag, html)

file_link =  s.group(1)

os.system('wget -P ' + dir_name + ' ' + file_link)


