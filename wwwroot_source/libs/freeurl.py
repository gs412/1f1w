#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import urllib
import urllib2
import web
from libs import utils

def postdata(port):
    while True:
        setting = web.config._setting
        if setting.freeurl_open == 'on':
            data = urllib.urlencode([('url',setting.freeurl_posturl),('username',setting.freeurl_username),('password',setting.freeurl_password),('sitename',setting.sitename.encode('utf-8')),('port',port)])
            try:
                req = urllib2.Request(setting.freeurl_posturl)
                fd = urllib2.urlopen(req, data)
            except:
                pass
                #print 'freeurl error'
        time.sleep(60)

def dopost(port):
    t = utils.ThreadSkeleton(postdata, port=port)
    t.start()