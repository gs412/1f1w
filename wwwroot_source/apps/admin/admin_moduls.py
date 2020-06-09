#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from time import time as now
import web
import conf
from conn import Bdb, db
from libs import utils
from moduls import moduls

class Thread:
    def __init__(self, *args, **kwargs):
        self.tid = kwargs.pop('tid', None)
    def get_hide_list(self, page):
        limit = 30
        offset = limit * (page - 1)
        threads = db.select('threads',
                            where='displayorder=-1',
                            order='tid desc',
                            limit=limit,
                            offset=offset).list()
        return threads
    def getcount(self):
        return db.query('select count(tid) as count from threads where displayorder=-1').list()[0].count
    def delete(self, tid):
        pids = db.select('posts',
                         where='tid=$tid',
                         vars=locals()).list()
        pids = [pid.pid for pid in pids]
        for pid in pids:
            Post().delete(pid)

        db.delete('threads',
                  where='tid=$tid',
                  vars=locals())

class Post:
    def __init__(self, *args, **kwargs):
        self.pid = kwargs.pop('pid', None)
    def get_hide_list(self, page):
        limit = 30
        offset = limit * (page - 1)
        posts = db.query('select p.*, t.* \
                          FROM posts p \
                          LEFT JOIN threads t ON t.tid=p.tid \
                          WHERE p.displayorder=-1 AND t.displayorder>=0 \
                          ORDER BY p.pid desc \
                          LIMIT $limit OFFSET $offset',
                          vars=locals()).list()
        return posts
    def getcount(self):
        return db.query('select count(p.pid) as count \
                         FROM posts p \
                         LEFT JOIN threads t on t.tid=p.tid \
                         WHERE p.displayorder=-1 AND t.displayorder>=0',
                         vars=locals()).list()[0].count
    def delete(self, pid):
        aids = db.select('attachments',
                         where='pid=$pid',
                         vars=locals()).list()
        aids = [aid.aid for aid in aids]
        for aid in aids:
            Attachment().delete(aid)

        db.delete('posts',
                  where='pid=$pid',
                  vars=locals())

class Attachment:
    def __init__(self, *args, **kwargs):
        self.aid = kwargs.pop('aid', None)
    def delete(self, aid):
        attachment = db.select('attachments',
                               where='aid=$aid',
                               vars=locals()).list()[0].attachment
        f = utils.realpath('sitedata/upload/attachment', attachment)
        os.remove(f)
        db.delete('attachments',
                  where='aid=$aid',
                  vars=locals())

class User:
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.pop('uid', None)
        self.username = kwargs.pop('username', None)
    def getlist(self, page):
        limit = 30
        offset = limit * (page - 1)
        users = db.select('users',
                          order='uid desc',
                          limit=limit,
                          offset=offset).list()
        return users
    def getcount(self):
        return db.query('select count(uid) as count from users').list()[0].count
    def delete(self, uid):
        tids = db.select('threads',
                         where='uid=$uid',
                         vars=locals()).list()
        tids = [tid.tid for tid in tids]
        for tid in tids:
            Thread().delete(tid)

        filedir = utils.realpath(utils.myfiledir(int(uid), 'face', '')[:-1])
        utils.delFiles(filedir)

        db.delete('users',
                  where='uid=$uid',
                  vars=locals())
        db.delete('userfields',
                  where='uid=$uid',
                  vars=locals())

class Invite:
    def __init__(self, *args, **kwargs):
        self.iid = kwargs.pop('iid', None)
        self.invite = kwargs.pop('invite', None)
        self.comment = kwargs.pop('comment', None)
    def add(self):
        return db.insert('invites',
                         invite=self.invite,
                         username='',
                         comment=self.comment,
                         createtime=int(now()),
                         usedtime=0)
    def get(self):
        return db.select('invites',
                         where='invite=$self.invite',
                         vars=locals()).list()
    def getinvites(self):
        db.delete('invites', where='createtime<'+str(int(now())-86400*7)+'')
        return db.select('invites', where='usedtime=0',order='iid desc').list()
    def getcount1(self):
        return db.query('select count(iid) as count from invites where usedtime=0').list()[0].count
    def getusedlist(self, page):
        limit = 30
        offset = limit * (page - 1)
        invites = db.select('invites',
                            order='usedtime desc',
                            where='usedtime>0',
                            limit=limit,
                            offset=offset).list()
        return invites
    def getcount2(self):
        return db.query('select count(iid) as count from invites where usedtime>0').list()[0].count
    def delete(self, iid):
        db.delete('invites',
                  where='iid=$iid',
                  vars=locals())
    def update(self, **kwargs):
        upstr = ','.join(['%s=%r'%(k,v) for k,v in kwargs.items()])
        db.query('update invites set ' + upstr + ' where iid=$self.iid', vars=locals())

