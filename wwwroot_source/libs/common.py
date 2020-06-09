#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import pickle
import random
import time
import web
import conf
from conn import Bdb
from moduls.moduls import User
from libs import utils

def get_setting():
    pkl_file = open(utils.realpath('sitedata/setting.pkl'), 'rb')
    web.config._setting = pickle.load(pkl_file)
    web.config._setting.version = conf.version
    pkl_file.close()
def set_setting():
    output = open(utils.realpath('sitedata/setting.pkl'), 'wb')
    pickle.dump(web.config._setting, output)
    output.close()

def check_login(*x):
    def newdeco(func):
        def function(*args, **kwargs):
            my = web.Storage()
            uid = web.cookies().get('uid')
            if uid is None:
                my.uid = 0
            else:
                uid, secret = uid.split('_')
                uid = int(uid)
                if uid == 0:
                    my.uid = 0
                else:
                    u = User(uid = uid).get()
                    if len(u) == 0:
                        my.uid = 0
                    else:
                        u = u[0]
                        lastlogintime, salt = str(u.lastlogintime), str(u.salt)
                        if secret == utils.sha1(utils.sha1(str(uid))+utils.sha1(lastlogintime)+utils.sha1(salt)+utils.sha1(conf.cookies_secret_key)):
                            my = u
                            del my.password, my.salt
                        else:
                            my.uid = 0
            if my.uid == 0:
                web.setcookie('uid', '0_0', 86400)
                my.groupid = 0
            my.limit = eval('web.config._setting.group.g' + str(my.groupid))
            my.chat_open = web.config._setting.chat_open
            my.env = web.ctx.env
            if 'must_chatopen' in x:
                if my.uid == 0:
                    return showmsg(u'请先 <a href=/login/><font color=blue><u>登录</u></font></a>')
                elif my.chat_open == '0':
                    return showmsg(u'群已经关闭')
            if 'must_admin' in x and my.groupid != 4:
                return showmsg(u'您不是管理员')
            elif 'must_login' in x and my.uid == 0:
                return showmsg(u'请先 <a href=/login/><font color=blue><u>登录</u></font></a>')
            else:
                if my.uid == 0:
                    my.username = ''
                function.my = my
                return func(*args, **kwargs)
        return function
    return newdeco

@check_login()
def showmsg(msg, **kwargs):
    setting = web.config._setting
    my = showmsg.my
    key = utils.authkey()

    rtitle = kwargs.pop('rtitle', None)
    referer = kwargs.pop('referer', None)
    redirect = kwargs.pop('redirect', None)

    d=locals()
    return conf.render.msg(**d)

def ok(*args):
    if len(args) == 0:
        url = ''
    else:
        if args[0] == 'back':
            url = web.ctx.env.get('HTTP_REFERER', '/')
        else:
            url = args[0]
    url = url.split('?rand=')[0]
    url = url+'?rand='+str(time.time()).replace('.','')+str(random.randint(100000,999999))
    return '<script>alert("OK");window.location="'+url+'";</script>'
