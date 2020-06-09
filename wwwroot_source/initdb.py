#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
import web
import conf
from conn import db
from libs import utils
from libs.common import *

def initdb():
    while True:
        a = ''
        a = raw_input('Initdb will clean all data in database, continue? (Y/N):').upper().strip()
        if a in ('Y','N','YES','NO'):
            if a in ('Y','YES'):
                if os.path.isfile(utils.realpath('sitedata/db.db')):
                    os.remove(utils.realpath('sitedata/db.db'))
                utils.delFiles(utils.realpath('sitedata/bsddb'))
                utils.delFiles(utils.realpath('apps/chat/sitedata/bsddb'))
        
                with file(utils.realpath('schema.sql'), 'r') as f:
                    sqltext = f.read()
                sqllist = sqltext.split(';')
                for sql in sqllist:
                    db.query(sql)
                
                get_setting()
                web.config._setting.usercount = 0
                set_setting()
                print 'success ^_^'
            break

if __name__ == "__main__":
    initdb()