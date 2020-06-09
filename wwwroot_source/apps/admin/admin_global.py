#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import web
import conf
from conn import Bdb, db
from libs.common import *
from libs import utils
from apps.admin import appconf
from apps.admin import admin_moduls

class Index:
    @check_login('must_admin')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my

        d=locals();d.pop('self')
        return appconf.render.index(**d)
    @check_login('must_admin')
    def POST(self):
        my = self.POST.my

        post = web.input()
        web.config._setting.sitename = post.sitename
        web.config._setting.reg_open = post.reg_open if 'reg_open' in post else ''
        web.config._setting.reg_seccode = post.reg_seccode if 'reg_seccode' in post else ''
        web.config._setting.reg_invite = post.reg_invite if 'reg_invite' in post else ''
        web.config._setting.reg_email = post.reg_email if 'reg_email' in post else ''
        web.config._setting.smtp_server = post.smtp_server
        web.config._setting.smtp_port = int(post.smtp_port)
        web.config._setting.smtp_username = post.smtp_username
        web.config._setting.smtp_password = post.smtp_password
        web.config._setting.freeurl_open = post.freeurl_open if 'freeurl_open' in post else ''
        web.config._setting.freeurl_posturl = post.freeurl_posturl
        web.config._setting.freeurl_domain = post.freeurl_domain
        web.config._setting.freeurl_username = post.freeurl_username
        web.config._setting.freeurl_password = post.freeurl_password
        set_setting()
        
        web.config.smtp_server = web.config._setting.smtp_server
        web.config.smtp_port = web.config._setting.smtp_port
        web.config.smtp_username = web.config._setting.smtp_username
        web.config.smtp_password = web.config._setting.smtp_password
        web.config.smtp_starttls = True

        return ok()

class Invite:
    @check_login('must_admin')
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        page = 1 if not page else int(page.rstrip('/'))

        if setting.reg_invite != 'on':
            return showmsg(u'已取消邀请码限制')

        inv = admin_moduls.Invite(
        )
        I1 = inv.getinvites()
        for i in I1:
            i.createtime = utils.format_datetime(i.createtime)
        I2 = inv.getusedlist(page)
        for i in I2:
            i.createtime = utils.format_datetime(i.createtime)
            i.usedtime = utils.format_datetime(i.usedtime)
        count = inv.getcount2()
        pagecount = int((count + 30 - 1)/30)
        pagestr = utils.multi(page, pagecount, '/admin/invite/')

        d=locals();d.pop('self')
        return appconf.render.invite(**d)
    @check_login('must_admin')
    def POST(self, page):
        setting = web.config._setting
        my = self.POST.my

        if setting.reg_invite != 'on':
            return showmsg(u'已取消邀请码限制')

        post = web.input()
        inv = admin_moduls.Invite(invite=''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',16)),
                                 comment=post.comment[:20],
        )
        if inv.getcount1() >= 10:
            return showmsg(u'最多允许存在10个有效邀请码，请先把邀请码的送出去或删除一部分再生成', referer='back')
        inv.add()
        return ok()

class Invitedelete:
    @check_login('must_admin')
    def GET(self, iid):
        inv = admin_moduls.Invite()
        inv.delete(iid)

        return ok('/admin/invite/')


class Userlist:
    @check_login('must_admin')
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        page = 1 if not page else int(page.rstrip('/'))

        users = admin_moduls.User().getlist(page)
        count = admin_moduls.User().getcount()
        pagecount = int((count+30-1)/30)
        pagestr = utils.multi(page, pagecount, '/admin/user/')

        d=locals();d.pop('self')
        return appconf.render.user(**d)

class Userdelete:
    @check_login('must_admin')
    def GET(self, uid):
        setting = web.config._setting
        my = self.GET.my
        
        if int(uid) == my.uid:
            return showmsg(u'不能删除自己', referer='back')

        admin_moduls.User().delete(uid)

        return ok('/admin/user/')

class Group:
    @check_login('must_admin')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my

        d=locals();d.pop('self')
        return appconf.render.group(**d)
    @check_login('must_admin')
    def POST(self):
        setting = web.config._setting
        my = self.POST.my

        post = web.input()

        g2 = web.Storage()
        g2.visit = post.group_g2_visit if 'group_g2_visit' in post else ''
        g2.view = post.group_g2_view if 'group_g2_view' in post else ''
        g2.post = post.group_g2_post if 'group_g2_post' in post else ''
        g2.seccode = post.group_g2_seccode if 'group_g2_seccode' in post else ''
        g2.upattach = post.group_g2_upattach if 'group_g2_upattach' in post else ''
        g2.downattach = post.group_g2_downattach if 'group_g2_downattach' in post else ''

        g1 = web.Storage()
        g1.visit = post.group_g1_visit if 'group_g1_visit' in post else ''
        g1.view = post.group_g1_view if 'group_g1_view' in post else ''
        g1.post = post.group_g1_post if 'group_g1_post' in post else ''
        g1.seccode = post.group_g1_seccode if 'group_g1_seccode' in post else ''
        g1.upattach = post.group_g1_upattach if 'group_g1_upattach' in post else ''
        g1.downattach = post.group_g1_downattach if 'group_g1_downattach' in post else ''

        g0 = web.Storage()
        g0.visit = post.group_g0_visit if 'group_g0_visit' in post else ''
        g0.view = post.group_g0_view if 'group_g0_view' in post else ''
        g0.post = post.group_g0_post if 'group_g0_post' in post else ''
        g0.seccode = post.group_g0_seccode if 'group_g0_seccode' in post else ''
        g0.upattach = post.group_g0_upattach if 'group_g0_upattach' in post else ''
        g0.downattach = post.group_g0_downattach if 'group_g0_downattach' in post else ''

        g4 = web.Storage()
        for attr in g2:
            exec('g4.'+attr+' = "on"')
        g4.seccode = ''

        group = web.Storage()
        group.g4 = g4
        group.g2 = g2
        group.g1 = g1
        group.g0 = g0

        web.config._setting.group = group
        set_setting()

        return ok()









