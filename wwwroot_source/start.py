#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import platform
import sys
import web
import apps
from libs import freeurl, utils
from libs.common import get_setting

urls = (
    '/(\d*\/?)', 'index.Index',
    '/index/add/', 'index.Add',
    '/index/reply/', 'index.Reply',
    '/login/', 'login.Login',
    '/logout/', 'login.Logout',
    '/losspass/', 'login.Losspass',
    '/losspass/setnewpass/(\d+)/(.+)/', 'login.Setnewpass',
    '/post/(\d+)/(\d*\/?)', 'index.Postview',
    '/post/delete/(\d+)/', 'index.Postdelete',
    '/post/settop/(\d+)/', 'index.Postsettop',
    '/post/canceltop/(\d+)/', 'index.Postcanceltop',
    '/profiles/activate/', 'profiles.Activate',
    '/profiles/email/', 'profiles.Email',
    '/profiles/face/', 'profiles.Face',
    '/profiles/password/', 'profiles.Password',
    '/profiles/sign/', 'profiles.Sign',
    '/register/', 'login.Register',
    '/register/activate/(\d+)/(.+\/?)', 'login.Activate',
    '/register/email/(\d+)/(.+)/(.+\/?)', 'login.Acemail',
    '/seccode/', 'libs.seccode.Seccode',
    '/seccode/check/(.+)/\d+/', 'libs.seccode.Seccodecheck',
    '/showfile/(.+)', 'index.Showfile',
    '/downfile/(\d+)/', 'index.Downfile',
    '/chat/', apps.chat.start.app,
    '/admin/', apps.admin.start.app,
    '', 'index.NoPage',
)

app = web.application(urls, globals())

if '_setting' not in web.config:
    get_setting()

web.config.smtp_server = web.config._setting.smtp_server
web.config.smtp_port = web.config._setting.smtp_port
web.config.smtp_username = web.config._setting.smtp_username
web.config.smtp_password = web.config._setting.smtp_password
web.config.smtp_starttls = True

session = web.session.Session(app, web.session.DiskStore(utils.realpath('sitedata/sessions')))
def session_hook():
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))


if platform.system() == 'Windows':
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    send_head = SimpleHTTPRequestHandler.send_head
    def new_send_head(*a, **kw):
        f = send_head(*a, **kw)
        return f and open(f.name, 'rb')
    SimpleHTTPRequestHandler.send_head = new_send_head


if len(sys.argv) > 1:
    freeurl.dopost(sys.argv[1])


if __name__ == '__main__':
    #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
