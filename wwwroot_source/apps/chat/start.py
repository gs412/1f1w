#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import web
from conn import Bdb
from libs import utils
from . import appconf

urls = (
    '', 'index.Index',
    'ajax/announce/\d*\/?', 'index.Announce',
    'ajax/getmsg/(\d+)/\d+/', 'index.Getmsg',
    'ajax/getmylastid2/\d+/', 'index.Getmylastid2',
    'ajax/getonline/\d+/', 'index.Getonline',
    'ajax/initkey/(\d+)/', 'index.Init_key',
    'ajax/listen/\d+/', 'index.Listen',
    'ajax/postmsg/', 'index.Postmsg',
    'msgs/(\d*\/?)', 'index.Msgs',
)
urls = utils.handle_app_urls(__file__, urls)

web.config.chat_online_mark = 0
web.config.chat_online_list = []
def up_chat_online_list():
    while True:
        online = Bdb('online')
        online.siteroot = appconf.SITE_ROOT
        online_view = Bdb('online_view')
        online_view.siteroot = appconf.SITE_ROOT
        for k,v in online.getall():
            if time.time() - float(v) > 2:
                online.delete(k)
            if online_view.has_key(k):
                if time.time()-float(v) > 2:
                    online_view.delete(k)
                    web.config.chat_online_mark += 1
            else:
                online_view.set(k, v)
                web.config.chat_online_mark += 1
        web.config.chat_online_list = [k for k, v in sorted(online_view.getall(), key=lambda x:x[1])]
        time.sleep(1)
t = utils.ThreadSkeleton(up_chat_online_list)
t.start()

app = web.application(urls, locals())