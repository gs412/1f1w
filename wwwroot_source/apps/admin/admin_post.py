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
        return appconf.render.post(**d)
    @check_login('must_admin')
    def POST(self):
        my = self.GET.my

        post = web.input()
        web.config._setting.perpage_list = int(post.perpage_list)
        web.config._setting.perpage_post = int(post.perpage_post)
        web.config._setting.authcode_open = post.authcode_open
        set_setting()

        return ok()

class Deletedthread:
    @check_login('must_admin')
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        page = 1 if not page else int(page.rstrip('/'))

        threads = admin_moduls.Thread().get_hide_list(page)
        count = admin_moduls.Thread().getcount()
        pagecount = int((count+30-1)/30)
        pagestr = utils.multi(page, pagecount, '/admin/deletedthread/')

        d=locals();d.pop('self')
        return appconf.render.deletedthread(**d)

class Threaddelete:
    @check_login('must_admin')
    def GET(self, tid):
        setting = web.config._setting
        my = self.GET.my

        admin_moduls.Thread().delete(tid)

        return ok('back')

class Deletedpost:
    @check_login('must_admin')
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        page = 1 if not page else int(page.rstrip('/'))

        posts = admin_moduls.Post().get_hide_list(page)
        count = admin_moduls.Post().getcount()
        pagecount = int((count+30-1)/30)
        pagestr = utils.multi(page, pagecount, '/admin/deletedpost/')

        d=locals();d.pop('self')
        return appconf.render.deletedpost(**d)

class Postdelete:
    @check_login('must_admin')
    def GET(self, pid):
        setting = web.config._setting
        my = self.GET.my

        admin_moduls.Post().delete(pid)

        return ok('back')















