#!/usr/bin/python
# -*- coding: UTF-8 -*-

from time import time as now
import random
import web
import conf
from conn import db, Bdb
from libs import utils

class Thread:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title', None)
        self.tid = kwargs.pop('tid', None)
        self.uid = kwargs.pop('uid', None)
        self.username = kwargs.pop('username', None)
        self.dateline = kwargs.pop('dateline', None)
        self.ip = kwargs.pop('ip', None)
    def add(self):
        postcount = Bdb('post_count')
        postcount.update('threads')
        return db.insert('threads',
                         title=self.title,
                         uid=self.uid,
                         username=self.username,
                         replies=0,
                         views=0,
                         displayorder=0,
                         dateline=self.dateline,
                         lastpost=self.dateline,
                         ip=self.ip,
                         attachment=0)
    def get(self):
        T = db.select('threads',
                      where='tid=$self.tid AND displayorder>=0',
                      vars=locals()).list()
        if len(T)>0:
            views = Bdb('post_views')
            T[0].views = views.update(self.tid)
        return T
    def update(self, **kwargs):
        upstr = ','.join(['%s=%r'%(k,v.encode(conf.charset) if isinstance(v,unicode) else v) for k,v in kwargs.items()])
        db.query('update threads set ' + upstr + ' where tid=$self.tid', vars=locals())
    def hide(self, tid):
        count = Bdb('post_count')
        threads = int(count.get('threads'))
        if threads > 0:
            count.set('threads', threads - 1)
        db.update('threads',
                  displayorder=-1,
                  where='tid=$tid',
                  vars=locals())

class Post:
    def __init__(self, *args, **kwargs):
        self.tid = kwargs.pop('tid', None)
        self.uid = kwargs.pop('uid', None)
        self.username = kwargs.pop('username', None)
        self.content = kwargs.pop('content', None)
        self.dateline = kwargs.pop('dateline', None)
        self.ip = kwargs.pop('ip', None)
        self.limit = web.config._setting.perpage_post
        self.page = kwargs.pop('page', None)
    def add(self):
        postcount = Bdb('post_count')
        postcount.update('posts')
        db.query('update threads set replies=replies+1, lastpost=$self.dateline, lastpostuser=$self.username where tid=$self.tid', vars=locals())
        floor = db.select('threads', what='replies', where='tid=$self.tid', vars=locals()).list()[0].replies
        return db.insert('posts',
                         tid=self.tid,
                         uid=self.uid,
                         username=self.username,
                         content=self.content,
                         floor=floor,
                         displayorder=0,
                         dateline=self.dateline,
                         ip=self.ip,
                         attachment=0)
    def get(self):
        offset = self.limit * (self.page - 1)
        posts = db.query('select p.*, u.uid, u.username, uf.uid, uf.face, uf.sightml \
                        FROM posts p \
                        LEFT JOIN users u ON u.uid=p.uid \
                        LEFT JOIN userfields uf ON uf.uid=u.uid \
                        WHERE p.tid=$self.tid AND p.displayorder>=0 \
                        ORDER BY p.pid ASC \
                        LIMIT $self.limit OFFSET $offset',
                        vars = locals()).list()
        attachpids = []
        for post in posts:
            if post.attachment == 1:
                attachpids.append(str(post.pid))
        if len(attachpids) > 0:
            attachpids = ','.join(attachpids)
            attachments = db.select('attachments',
                                    where='pid in ('+attachpids+')').list()
            attachdict = {}
            for attachment in attachments:
                attachdict.setdefault(attachment.pid, attachment)
            for post in posts:
                if post.attachment == 1:
                    post.attach = attachdict[post.pid]
        
        return posts
    def hide(self, pid):
        db.update('posts',
                  displayorder=-1,
                  where='pid=$pid',
                  vars=locals())
        post = db.select('posts', where='pid=$pid', vars=locals()).list()[0]
        if post.floor == 1:
            Thread().hide(post.tid)
        else:
            db.query('update threads set replies=replies-1 where tid=$post.tid', vars=locals())
            
    
class Attachment:
    def __init__(self, *args, **kwargs):
        self.tid = kwargs.pop('tid', 0)
        self.pid = kwargs.pop('pid', 0)
        self.uid = kwargs.pop('uid', 0)
        self.dateline = kwargs.pop('dateline', 0)
        self.filename = kwargs.pop('filename', None)
        self.filesize = kwargs.pop('filesize', 0)
        self.attachment = kwargs.pop('attachment', None)
        self.isimage = kwargs.pop('isimage', 0)
        self.imwidth = kwargs.pop('imwidth', 0)
        self.thumb = kwargs.pop('thumb', 0)
    def add(self):
        db.query('update threads set attachment=1 where tid=$self.tid', vars=locals())
        db.query('update posts set attachment=1 where pid=$self.pid', vars=locals())
        return db.insert('attachments',
                         tid = self.tid,
                         pid = self.pid,
                         uid = self.uid,
                         dateline = self.dateline,
                         filename = self.filename,
                         filesize = self.filesize,
                         attachment = self.attachment,
                         downloads = 0,
                         isimage = self.isimage,
                         width = self.imwidth,
                         thumb = self.thumb)
    def get(self, aid):
        db.query('update attachments set downloads=downloads+1 where aid=$aid', vars=locals())
        return db.select('attachments',
                         where='aid=$aid',
                         vars=locals()).list()[0]

class Threadlist:
    def __init__(self, *args, **kwargs):
        self.Threads = None
        self.page = kwargs.pop('page', None)
    def getlist(self):
        limit = web.config._setting.perpage_list
        offset = limit * (self.page - 1)
        self.Threads = db.select('threads',
                                 where='displayorder>=0',
                                 order='displayorder desc, lastpost desc',
                                 limit=limit,
                                 offset=offset).list()
        self.__getviews()
        return self.Threads
    def __getviews(self):
        tidlist = list()
        for thread in self.Threads:
            tidlist.append(thread.tid)
        views = Bdb('post_views')
        viewsdict = views.getdict(tidlist)
        for thread in self.Threads:
            thread.views = viewsdict[thread.tid]
    def getcount(self):
        count = Bdb('post_count')
        threads = int(count.get('threads'))
        posts = int(count.get('posts'))
        return threads, posts

class User:
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.pop('uid', None)
        self.username = kwargs.pop('username', None)
    def add(self):
        salt = random.randint(100000,999999)
        password = utils.sha1(utils.sha1(self.password)+str(salt))
        ip = web.ctx.ip
        dateline = int(now())
        return db.insert('users',
                         username = self.username,
                         password = password,
                         groupid = self.groupid,
                         email = self.email,
                         gender = self.gender,
                         regip = ip,
                         lastloginip = ip,
                         regdate = dateline,
                         lastlogintime = dateline,
                         salt = salt)
    def addfields(self):
        db.insert('userfields',
                  uid = self.uid,
                  face = self.face,
                  sightml = self.sightml,
                  activate = self.activate)
    def existname(self):
        return len(db.select('users', where='username=$self.username', vars=locals()).list())
    def existemail(self):
        return len(db.select('users', where='email=$self.email AND groupid=2', vars=locals()).list())
    def existemail2(self, uid, email):
        return len(db.select('users', where='email=$email AND uid<>$uid AND groupid=2', vars=locals()).list())
    def get(self):
        if self.uid is not None:
            where = 'uid=$self.uid'
        elif self.username is not None:
            where = 'username=$self.username'
        else:
            print '<moduls.moduls.User.get has no uid or username>'
            return None
        return db.select('users', where=where, vars=locals()).list()
    def getcount(self):
        return db.query('select count(*) as count from users').list()[0].count
    def getfields(self):
        return db.select('userfields', where='uid=$self.uid', vars=locals()).list()
    def update(self, **kwargs):
        upstr = ','.join(['%s=%s'%(k,"'%s'"%v.encode(conf.charset) if isinstance(v,(str,unicode)) else v) for k,v in kwargs.items()])
        db.query('update users set ' + upstr + ' where uid=$self.uid', vars=locals())
    def updatefields(self, **kwargs):
        upstr = ','.join(['%s=%s'%(k,"'%s'"%v.encode(conf.charset) if isinstance(v,(str,unicode)) else v) for k,v in kwargs.items()])
        db.query('update userfields set ' + upstr + ' where uid=$self.uid', vars=locals())














