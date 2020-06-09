#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import random
import time
import web
import conf
from conn import Bdb, db
from libs.common import *
from libs import utils
from . import appconf
from .moduls.moduls import Msg, Msglist

def set_mythreadid(uid):
    mythreadid = Bdb('mythreadid')
    mythreadid.siteroot = appconf.SITE_ROOT
    mythreadid.set(uid, str(time.time())+str(random.randint(100000,999999)))
def get_mythreadid(uid):
    mythreadid = Bdb('mythreadid')
    mythreadid.siteroot = appconf.SITE_ROOT
    return mythreadid.get(uid)

def get_dblast_mid():
    dblast = Bdb('dblast')
    dblast.siteroot = appconf.SITE_ROOT
    return int(dblast.get('dblast_mid'))
def set_mylastid(uid, lastid):
    mylastid = Bdb('mylastid')
    mylastid.siteroot = appconf.SITE_ROOT
    mylastid.set(uid, lastid)
def get_mylastid(uid):
    mylastid = Bdb('mylastid')
    mylastid.siteroot = appconf.SITE_ROOT
    return int(mylastid.get(uid))

def set_msgkey(uid, key):
    msgkey = Bdb('msgkey')
    msgkey.siteroot = appconf.SITE_ROOT
    msgkey.set(uid, key)
def get_msgkey(uid):
    msgkey = Bdb('msgkey')
    msgkey.siteroot = appconf.SITE_ROOT
    return msgkey.get(uid)

def set_myonlinemark(uid, mark):
    myonlinemark = Bdb('myonlinemark')
    myonlinemark.siteroot = appconf.SITE_ROOT
    myonlinemark.set(uid, mark)
def get_myonlinemark(uid):
    myonlinemark = Bdb('myonlinemark')
    myonlinemark.siteroot = appconf.SITE_ROOT
    return int(myonlinemark.get(uid))

class Init_key:
    @check_login('must_chatopen')
    def GET(self, key):
        my = self.GET.my
        set_msgkey(my.uid, key)
        return 'Init_key_ok'

class Index:
    @check_login('must_chatopen')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        key = utils.authkey()

        pageid = str(time.time()).replace('.','') + str(random.randint(100000,999999))
        self.__setpagemark(my.uid, pageid)
        stitle = utils.authcode(u'群聊 - '+setting.sitename, key, operation='ENCODE')
        announce = self.__getannounce()
        set_mylastid(my.uid, get_dblast_mid())
        set_myonlinemark(my.uid, 0)

        d=locals();d.pop('self')
        if 'MSIE 6' in my.env.get('HTTP_USER_AGENT', '0') or 'MSIE 7' in my.env.get('HTTP_USER_AGENT', '0'):
            return appconf.render.index_ie6(**d)
        else:
            return appconf.render.index(**d)
    def __setpagemark(self, uid, pageid):
        pagemark = Bdb('pagemark')
        pagemark.siteroot = appconf.SITE_ROOT
        pagemark.set(uid, pageid)
    def __getannounce(self):
        announce = Bdb('announce')
        announce.siteroot = appconf.SITE_ROOT
        return utils.htmlquote(announce.get('txt').decode('utf-8'))

class Postmsg:
    @check_login('must_chatopen')
    def POST(self):
        my = self.POST.my
        post = web.input()
        msgkey = get_msgkey(my.uid)
        msg = utils.authcode(post.msg, msgkey, operation='DECODE')
        if msg[:3] == 'key':
            m = Msg(username=my.username,
                    msg = msg[3:],
                    dateline = int(time.time())
            )
            m.add()
            return 'postmsgok'
        else:
            return 'wrongkey'

class Getmylastid2:
    @check_login('must_chatopen')
    def GET(self):
        my = self.GET.my
        if 'mylastid2' in web.ctx.session:
            set_mylastid(my.uid, web.ctx.session.mylastid2)
        return 'Getmylastid2 ok'

class Getmsg:
    @check_login('must_chatopen')
    def GET(self, pageid):
        my = self.GET.my
        msgkey = get_msgkey(my.uid)
        mylastid = get_mylastid(my.uid)
        if str(pageid) != self.__getpagemark(my.uid):
            return 'oldpage'
        m = Msg()
        li = m.getlist(mylastid)
        if len(li) == 0:
            return ''
        else:
            #web.ctx.session.mylastid2 = mylastid
            set_mylastid(my.uid, li[0]['mid'])
            for i, l in enumerate(li):
                l.dateline = time.strftime('%H:%M:%S', time.localtime(l.dateline))
                l.msg = utils.authcode(l.msg, msgkey, operation='ENCODE')
                li[i] = dict(l)
            return 'msg'+utils.authcode('key', msgkey, operation='ENCODE')+str(li)
    def __getpagemark(self, uid):
        pagemark = Bdb('pagemark')
        pagemark.siteroot = appconf.SITE_ROOT
        return pagemark.get(uid)

class Getonline:
    @check_login('must_chatopen')
    def GET(self):
        my = self.GET.my
        set_myonlinemark(my.uid, web.config.chat_online_mark)

        ol = web.config.chat_online_list
        ids = ','.join(ol)
        users = db.query('select u.uid,u.username,uf.uid,uf.face \
                          FROM users u \
                          LEFT JOIN userfields uf ON u.uid=uf.uid \
                          WHERE u.uid in ('+ids+')')
        user_d = {}
        for user in users:
            user.face, user.facewidth, user.faceheight = user.face.split('|')
            user.facewidth, user.faceheight = map(float, (user.facewidth, user.faceheight))
            if user.facewidth > user.faceheight:
                user.faceheight = user.faceheight * 16 / user.facewidth
                user.facewidth = 16
            else:
                user.facewidth = user.facewidth * 16 / user.faceheight
                user.faceheight = 16
            user_d.setdefault(user.uid, user)
        user_l = []
        for uid in ol:
            user_l.append(user_d[int(uid)])
        d=locals();d.pop('self')
        return appconf.render.onlinelist(**d)

class Listen:
    @check_login('must_chatopen')
    def GET(self):
        web.header('Content-type','text/html')
        web.header('Transfer-Encoding','chunked')
        yield 'XXXXXXXXXX'
        my = self.GET.my
        uid = my.uid
        set_mythreadid(uid)
        mylastid = get_mylastid(uid)
        mythreadid = get_mythreadid(uid)
        for i in xrange(100):
            #print i, get_dblast_mid(),mylastid, get_mythreadid(uid), mythreadid
            if get_dblast_mid() > mylastid:
                yield 'newmsg'
                break
            if get_mythreadid(uid) != mythreadid:
                #print 'close old thread'*100
                #print get_mythreadid(uid), mythreadid
                yield 'oldthread'
                break
            if i%5 == 0:
                online = Bdb('online')
                online.siteroot = appconf.SITE_ROOT
                online.set(uid, time.time())
                if get_myonlinemark(uid) != web.config.chat_online_mark:
                    yield 'onlinechanged'
                    break
            yield 'xxxxxx'
            time.sleep(0.1)
        yield 'comet'

class Announce:
    @check_login('must_chatopen')
    def GET(self):
        announce = Bdb('announce')
        announce.siteroot = appconf.SITE_ROOT
        return announce.get('txt')
    @check_login('must_admin')
    def POST(self):
        post = web.input()
        announce = Bdb('announce')
        announce.siteroot = appconf.SITE_ROOT
        announce.set('txt', post.announce.encode('utf-8'))
        return utils.htmlquote(post.announce)

class Msgs:
    @check_login('must_chatopen')
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        key = utils.authkey()

        msgscount = Msglist().getcount()
        pagecount = int((msgscount+20-1)/20)
        page = pagecount if not page else int(page.rstrip('/'))

        Msgs = Msglist(page=page,
        ).getlist()
        for m in Msgs:
            m.dateline = utils.format_datetime(m.dateline)
            m.msg = '<script>w(c("'+utils.authcode(m.msg, key, operation='ENCODE')+'"))</script>'
        pagestr = utils.multi(page, pagecount, '/chat/msgs/')
        stitle = utils.authcode(u'聊天记录 - '+setting.sitename, key, operation='ENCODE')

        d=locals();d.pop('self')
        return appconf.render.msglist(**d)

class NoPage:
    def GET(self):
        web.header('Content-Type', 'text/html; charset=%s' % conf.charset)
        return u'网页不存在'
