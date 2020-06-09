#!/usr/bin/python
# -*- coding: UTF-8 -*-

import web
import conf
from conn import Bdb, db
from libs.common import *
from libs import utils
from apps.admin import appconf

class Index:
    @check_login('must_admin')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my

        d=locals();d.pop('self')
        return appconf.render.chat(**d)
    @check_login('must_admin')
    def POST(self):
        my = self.POST.my

        post = web.input()
        web.config._setting.chat_open = post.chat_open
        set_setting()

        return ok()