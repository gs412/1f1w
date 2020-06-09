#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil

def delFiles(paths):
    li = []
    def VisitDir(arg, dirname, names):
        for filepath in names:
            li.append(os.path.join(dirname, filepath))
    os.path.walk(paths, VisitDir, ())
    li.reverse()
    for l in li:
        if os.path.isfile(l):
            os.remove(l)
        else:
            os.rmdir(l)
    os.rmdir(paths)

ROOT = os.path.dirname(os.path.abspath(__file__))

os.chdir(os.path.join(ROOT, 'pythonapp_source'))
os.system('python mysetup.py py2exe')
    
try:
    delFiles(os.path.join(ROOT, '1F1W'))
except:
    print 'del old 1f1w failed'

try:
    delFiles(os.path.join(ROOT, 'pythonapp_source', 'build'))
except:
    print 'del build failed'

try:
    shutil.move(os.path.join(ROOT, 'pythonapp_source', 'dist'), os.path.join(ROOT, '1F1W', 'pythonapp'))
except:
    print 'move dist failed'

os.system('xcopy ' + os.path.join(ROOT, 'wwwroot_source') + ' ' + os.path.join(ROOT, '1F1W', 'wwwroot\\') + '/S /E')

os.mkdir(os.path.join(ROOT, '1F1W', 'packages'))