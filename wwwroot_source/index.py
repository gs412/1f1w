#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cgi
import Image
import time
import web
import conf
from conn import db
from libs.common import *
from libs import utils
from moduls.moduls import *

class Index:
    @check_login()
    def GET(self, page):
        setting = web.config._setting
        my = self.GET.my
        key = utils.authkey()
        page = 1 if not page else int(page.rstrip('/'))
        if my.limit.visit != 'on':
            return showmsg(u'您所在的用户组无权限')

        Tlist = Threadlist(page=page,
        )
        T = Tlist.getlist()
        for t in T:
            if setting.authcode_open == '1':
                t.title = '<script>w(c("'+utils.authcode(t.title, key, operation='ENCODE')+'"))</script>'
            t.replies -= 1
            t.username = utils.ip_or_name(t.username)
            t.lastpost = self.__format_datetime(t.lastpost)
            t.lastpostuser = utils.ip_or_name(t.lastpostuser)
            t.ip = utils.ip_safe(t.ip)
        threads, posts = Tlist.getcount()
        perpage = setting.perpage_list
        pagecount = int((threads+perpage-1)/perpage)
        pagestr = utils.multi(page, pagecount, '/')
        if setting.authcode_open == '1':
            stitle = utils.authcode(u'帖吧 - '+setting.sitename, key, operation='ENCODE')
        else:
            stitle = None

        d=locals();d.pop('self')
        if setting.usercount == 0:
            return conf.render.index_admin_register(**d)
        else:
            return conf.render.index(**d)
    def __format_datetime(self, timestamp):
        if time.localtime(timestamp)[2] == time.localtime()[2]:
            return time.strftime('%H:%M', time.localtime(timestamp))
        else:
            return time.strftime('%m-%d', time.localtime(timestamp))

class Add:
    @check_login()
    def POST(self):
        setting = web.config._setting
        ip = web.ctx.ip
        my = self.POST.my
        if my.limit.post != 'on':
            return showmsg(u'您所在的用户组无权限')
        if my.uid == 0:
            my.username = ip
        key = utils.authkey()
        cgi.maxlen = 1024 * 1024 * 5
        try:
            post = web.input(attach={})
        except:
            return showmsg(u'附件太大(最大5M)', referer='back')
        if my.limit.seccode == 'on':
            if post.secinput.upper() != web.ctx.session.seccode.upper():
                return showmsg(u'验证码错误', referer='back')
            del web.ctx.session.seccode
        if post.title == '':
            return showmsg(u'帖子标题不能为空！', referer='back')
        elif post.content == '' and post.attach.filename == '':
            return showmsg(u'帖子内容不能为空！', referer='back')
        dateline = int(time.time())
        t = Thread(title=utils.authcode(post.title, key, operation='DECODE'),
                   uid=my.uid,
                   username=my.username,
                   dateline=dateline,
                   ip=ip,
        )
        tid = t.add()
        p = Post(tid=tid,
                 uid=my.uid,
                 username=my.username,
                 content=utils.authcode(post.content, key, operation='DECODE'),
                 dateline=dateline,
                 ip=ip,
        )
        pid = p.add()
        if post.attach.filename != '' and my.limit.upattach == 'on':
            upload_attach(tid, pid, my.uid, dateline, post.attach)
        return utils.redirect('/')
    def _test_post(self):
        dateline = int(time.time())
        ip = '222.222.222.222'
        t = Thread(title='post.title',
                   dateline=dateline,
                   ip=ip,
        )
        tid = t.add()
        p = Post(tid=tid,
                 content='post.content',
                 dateline=dateline,
                 ip=ip,
        )
        p.add()

class Reply:
    @check_login()
    def POST(self):
        setting = web.config._setting
        ip = web.ctx.ip
        my = self.POST.my
        key = utils.authkey()
        if my.limit.post != 'on':
            return showmsg(u'您所在的用户组无权限')
        if my.uid == 0:
            my.username = ip
        cgi.maxlen = 1024 * 1024 * 5
        try:
            post = web.input(attach={})
        except:
            return showmsg(u'附件太大(最大5M)', referer='back')
        if my.limit.seccode == 'on':
            if post.secinput.upper() != web.ctx.session.seccode.upper():
                return showmsg(u'验证码错误', referer='back')
            del web.ctx.session.seccode
        if post.content == '' and post.attach.filename == '':
            return showmsg(u'回复内容不能为空！', referer='back')
        dateline = int(time.time())
        p = Post(tid=post.tid,
                 uid=my.uid,
                 username=my.username,
                 content=utils.authcode(post.content, key, operation='DECODE'),
                 dateline=dateline,
                 ip=ip,
        )
        pid = p.add()
        if post.attach.filename != '' and my.limit.upattach == 'on':
            upload_attach(post.tid, pid, my.uid, dateline, post.attach)
        return utils.redirect(utils.get_referer())
    def _test_reply(self):
        p = Post(tid=604,
                 content='post.content',
                 dateline=int(time.time()),
                 ip='222.222.222.222',
        )
        p.add()

def upload_attach(tid, pid, uid, dateline, attach):
    filedir = utils.realpath('sitedata/upload/attachment', time.strftime('%Y/%m/%d', time.localtime(dateline)))
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    #rfile = '%s/%s_%s.%s' % (filedir, dateline, random.randint(100000,999999), attach.filename.split('.')[-1])
    fileext = attach.filename.split('.')[-1]
    if fileext in ('jpg','jpeg','gif','png','bmp'):
        isimage = 1
    else:
        isimage = 0
        fileext = 'txt'
    rfile = '%s/%s_%s.%s' % (filedir, dateline, random.randint(100000,999999), fileext) #for safe
    fout = open(rfile, 'wb')
    fout.write(attach.file.read())
    fout.close()

    filesize = os.path.getsize(rfile)
    attachment = rfile.split('attachment')[1][1:]
    imwidth = thumb = 0
    if isimage == 1:
        im = Image.open(rfile)
        imwidth = im.size[0]
        if imwidth > 570:
            imwidth = 570
            thumb = 1
    a = Attachment(tid = tid,
                   pid = pid,
                   uid = uid,
                   dateline = dateline,
                   filename = attach.filename,
                   filesize = filesize,
                   attachment = attachment,
                   isimage = isimage,
                   imwidth = imwidth,
                   thumb = thumb,
    )
    a.add()

class Postview:
    @check_login()
    def GET(self, tid, page):
        setting = web.config._setting
        my = self.GET.my
        key = utils.authkey()
        page = 1 if not page else int(page.rstrip('/'))
        if my.limit.view != 'on':
            return showmsg(u'您所在的用户组无权限')

        tid = int(tid)
        p = Post(tid=tid,
                 page=page,
        )
        P = p.get()
        if len(P) == 0 or P[0].floor > 1:
            return showmsg(u'帖子不存在或已被删除')
        for p in P:
            if p.uid > 0:
                p.face, p.facewidth, p.faceheight = p.face.split('|')
            if p.username is None:
                p.username = utils.ip_safe(p.ip)
            p.content = utils.htmlquote(p.content)
            if setting.authcode_open == '1':
                p.content = '<script>w(c("'+utils.authcode(p.content, key, operation='ENCODE')+'"))</script>'
            p.dateline = utils.format_datetime(p.dateline)
        t = Thread(tid=tid,
        )
        T = t.get()
        if len(T) == 0: raise web.notfound()
        T = T[0]
        pcount = T.replies
        perpage = setting.perpage_post
        pagecount = int((pcount+perpage-1)/perpage)
        pagestr = utils.multi(page, pagecount, '/post/'+str(tid)+'/')
        if setting.authcode_open == '1':
            stitle = utils.authcode(T.title+' - '+setting.sitename, key, operation='ENCODE')
            T.title = '<script>w(c("'+utils.authcode(T.title, key, operation='ENCODE')+'"))</script>'
        else:
            stitle = None

        d=locals();d.pop('self')
        return conf.render.post(**d)

class Postdelete:
    @check_login('must_admin')
    def GET(self, pid):
        Post().hide(pid)
        return ok('back')

class Postsettop:
    @check_login('must_admin')
    def GET(self, tid):
        Thread(tid=tid,
        ).update(displayorder=1)
        return ok('back')

class Postcanceltop:
    @check_login('must_admin')
    def GET(self, tid):
        Thread(tid=tid,
        ).update(displayorder=0)
        return ok('back')

class Showfile:
    def GET(self, f):
        f = utils.realpath('sitedata/upload', f)
        environ = web.ctx.env
        if environ.get('HTTP_HOST', 'host') in environ.get('HTTP_REFERER', 'referer'):
            if os.path.isfile(f):
                ftype = f.split('.')[-1]
                web.header('Content-Type','image/%s' % ftype)
                image = open(f, 'rb').read()
            else:
                return showmsg(u'附件已被删除')
        else:
            web.header('Content-Type','image/gif')
            image = open(utils.realpath('static/img/fangdaolian.gif'), 'rb').read()
        return image

class Downfile:
    @check_login()
    def GET(self, aid):
        my = self.GET.my
        if my.limit.downattach != 'on':
            return showmsg(u'您所在的用户组无权限')
        if my.env.get('HTTP_HOST', 'host') in my.env.get('HTTP_REFERER', 'referer'):
            a = Attachment().get(aid)
            f = utils.realpath('sitedata/upload/attachment', a.attachment)
            if os.path.isfile(f):
                web.header('Content-Disposition','filename=%s' % a.filename.encode('gbk'))
                web.header('Content-Type','application/octet-stream')
                web.header('Content-Length',a.filesize)
                returnfile = open(f, 'rb').read()
            else:
                return showmsg(u'附件已被删除')
        else:
            web.header('Content-Type','image/gif')
            returnfile = open('static/img/fangdaolian.gif', 'rb').read()
        return returnfile

class NoPage:
    def GET(self,args):
        web.header('Content-Type','text/html; charset=%s' % conf.charset)
        return showmsg(u'页面不存在')

if __name__ == '__main__':
    x = 2
    if x == 1:
        a = Add()
        for i in xrange(600):
            a._test_post()
    else:
        r = Reply()
        for i in xrange(500):
            r._test_reply()
