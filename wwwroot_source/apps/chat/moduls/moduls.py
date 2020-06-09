#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
from conn import db, Bdb
from .. import appconf

class Msg:
    def __init__(self, *agrs, **kwargs):
        self.username = kwargs.pop('username', None)
        self.msg = kwargs.pop('msg', None)
        self.dateline = kwargs.pop('dateline', None)
    def add(self):
        mid = db.insert('chat_msg',
                        username = self.username,
                        msg = self.msg,
                        dateline = self.dateline)
        dblast = Bdb('dblast')
        dblast.siteroot = appconf.SITE_ROOT
        dblast.set('dblast_mid', mid)
        return mid
    def getlist(self, mylastid):
        return db.select('chat_msg',
                         order = 'mid desc',
                         limit = 100,
                         where = 'mid > $mylastid',
                         vars = locals()).list()
    
class Msglist:
    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page', None)
    def getlist(self):
        limit = 20
        offset = limit * (self.page - 1)
        self.Msgs = db.select('chat_msg',
                              order='mid asc',
                              limit=limit,
                              offset=offset).list()
        return self.Msgs
    def getcount(self):
        return db.query('select count(*) as count from chat_msg').list()[0].count

