#!/usr/bin/python
#encoding=utf-8

import os
import sys
import thread
import time

sys.stdout = open("l_stdout.log", "w")
sys.stderr = open("l_stdout.log", "w")

mainpath = os.path.dirname(os.getcwd())
sitepath = mainpath + "\wwwroot"
script = "start.py"
app_path = mainpath + "\pythonapp"

if os.path.isdir(mainpath + "\packages"):
    sys.path.append(mainpath + "\packages")

def startserver(sitepath,script):
    sys.argv = [0,sys.argv[1]]
    sys.path.append(sitepath)
    os.chdir(sitepath)
    execfile(script,globals())

thread.start_new_thread(startserver,(sitepath,script))

n = 0
while True:
    n = n + 1
    if n > 100:
        n = 0
        time1 = os.stat(app_path+"\l_alive.log").st_mtime
        if abs(time.time() - time1) > 200:
            thread.exit()
    f = open(app_path+"\l_stop.log")
    process = f.read()
    f.close
    if process == 'stop':
        thread.exit()
    time.sleep(1)