#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
from time import time as now
import web
import conf
from conn import db
from libs.common import *
from libs import utils
from moduls.moduls import User

def addfields(my):
    u = User(uid=my.uid)
    my.update(u.getfields()[0])
    my.face, my.facewidth, my.faceheight = my.face.split('|')
    return my

class Email:
    @check_login('must_login')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        my = addfields(my)

        d=locals();d.pop('self')
        return conf.render.profiles_email(**d)

    @check_login('must_login')
    def POST(self):
        setting = web.config._setting
        my = self.POST.my
        my = addfields(my)

        post = web.input()
        if User().existemail2(my.uid, post.newemail) and setting.reg_email == 'on':
            return showmsg(u'邮箱已被别人使用, 请更换一个新的邮箱', referer='back')
        my.actime, my.acstr = my.activate.split('|')
        if int(now()) - int(my.actime) < 60 * 15:
            return showmsg(u'您刚刚修改了邮箱, 请15分钟后再更改', referer='back')

        u = User(uid=my.uid,
        )
        user = u.get()[0]
        if user.password != utils.sha1(utils.sha1(post.oldpass)+str(user.salt)):
            return showmsg(u'当前密码错误', referer='back')
        elif post.newemail != post.verifyemail:
            return showmsg(u'两次输入的邮箱不一致', referer='back')
        elif post.newemail == my.email:
            return showmsg(u'新邮箱不能设置为原先的邮箱', referer='back')
        else:
            if setting.reg_email == 'on':
                activate = str(int(now())) + '|' + ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',20))
                u.updatefields(activate=activate)
                if my.groupid == 1:
                    u.update(email=post.newemail)
                subject = u'验证新邮箱'
                message = u'''
                请点击下面的链接验证您的新邮箱:

                http://%s/register/email/%s/%s/%s/

                (如果上面不是链接形式，请将地址手工粘贴到浏览器地址栏再访问)
                ''' % (my.env.get('HTTP_HOST'), my.uid, web.urlquote(post.newemail), web.urlquote(activate))

                try:
                    web.sendmail(web.config.smtp_username, post.newemail, subject, message)
                except Exception, e:
                    return e

                return showmsg(u'一封验证邮件已经发到您设置的新邮箱, 请按邮件中的链接验证新邮箱')
            else:
                u.update(email=post.newemail)
                return showmsg(u'新邮箱设置成功')

class Face:
    @check_login('must_login')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        my = addfields(my)

        d=locals();d.pop('self')
        return conf.render.profiles_face(**d)

    @check_login('must_login')
    def POST(self):
        my = self.POST.my
        import cgi
        cgi.maxlen = 1024 * 1024 * 5
        try:
            post = web.input(myface={})
        except ValueError:
            return showmsg(u'图片太大(最大5M)', referer='back')
        if post.myface.filename == '':
            return showmsg(u'没有选择图片', referer='back')
        else:
            filedir = utils.myfiledir(my.uid, 'face', 'face')
            utils.delFiles(filedir)
            filename = 'main.' + post.myface.filename.split('.')[-1]
            face = filedir + filename
            fout = open(face, 'wb')
            fout.write(post.myface.file.read())
            fout.close()

            facewidth, faceheight = utils.getimgsize(face, 120, 120)
            facerand = str(int(now())) + str(random.randint(10000,99999))
            face = '%s?v=%s|%s|%s' % (face.split('upload')[1][1:], facerand, facewidth, faceheight)
            u = User(uid=my.uid,
            )
            u.updatefields(face=face)
            return utils.redirect(my.env.get('HTTP_REFERER', '/'))

class Password:
    @check_login('must_login')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        my = addfields(my)

        d=locals();d.pop('self')
        return conf.render.profiles_password(**d)

    @check_login('must_login')
    def POST(self):
        my = self.POST.my
        post = web.input()

        u = User(uid=my.uid,
        )
        user = u.get()[0]
        if user.password != utils.sha1(utils.sha1(post.oldpass)+str(user.salt)):
            return showmsg(u'当前密码错误', referer='back')
        elif post.newpass == '':
            return showmsg(u'新密码不能为空', referer='back')
        elif post.newpass != post.verifypass:
            return showmsg(u'两次输入的新密码不一致', referer='back')
        else:
            newpass = utils.sha1(utils.sha1(post.newpass)+str(user.salt))
            u.update(password = newpass)
            return utils.redirect(my.env.get('HTTP_REFERER', '/'))


class Sign:
    @check_login('must_login')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        my = addfields(my)

        d=locals();d.pop('self')
        return conf.render.profiles_sign(**d)

    @check_login('must_login')
    def POST(self):
        my = self.POST.my
        import cgi
        cgi.maxlen = 1024 * 1024 * 5
        try:
            post = web.input(mysign={})
        except ValueError:
            return showmsg(u'图片太大(最大5M)', referer='back')
        if post.mysign.filename == '':
            return showmsg(u'没有选择图片', referer='back')
        else:
            filedir = utils.myfiledir(my.uid, 'face', 'sign')
            utils.delFiles(filedir)
            filename = 'main.' + post.mysign.filename.split('.')[-1]
            sign = filedir + filename
            fout = open(sign, 'wb')
            fout.write(post.mysign.file.read())
            fout.close()

            signwidth, signheight = utils.getimgsize(sign, 500, 200)
            signrand = str(int(now())) + str(random.randint(10000,99999))
            sightml = '<img src=/showfile/%s?v=%s width=%s height=%s border=0>' % (sign.split('upload')[1][1:], signrand, signwidth, signheight)
            u = User(uid=my.uid,
            )
            u.updatefields(sightml=sightml)
            return utils.redirect(my.env.get('HTTP_REFERER', '/'))

class Activate:
    @check_login('must_login')
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        my = addfields(my)

        d=locals();d.pop('self')
        return conf.render.profiles_activate(**d)
    @check_login('must_login')
    def POST(self):
        setting = web.config._setting
        my = self.POST.my
        my = addfields(my)

        if User().existemail2(my.uid, my.email):
            return showmsg(u'邮箱已被别人使用, 请 <a href="/profiles/email/">更换一个新的邮箱</a>')
        my.actime, my.acstr = my.activate.split('|')
        if int(now()) - int(my.actime) < 60 * 15:
            return showmsg(u'您刚刚修改了邮箱, 请15分钟后再更改', referer='back')

        u = User(uid=my.uid
        )
        activate = str(int(now())) + '|' + ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',20))
        u.updatefields(activate=activate)
        subject = u'验证新邮箱'
        message = u'''
        请点击下面的链接验证您的新邮箱:

        http://%s/register/email/%s/%s/%s/

        (如果上面不是链接形式，请将地址手工粘贴到浏览器地址栏再访问)
        ''' % (my.env.get('HTTP_HOST'), my.uid, web.urlquote(my.email), web.urlquote(activate))

        try:
            web.sendmail(web.config.smtp_username, my.email, subject, message)
        except Exception, e:
            return e

        return showmsg(u'一封验证邮件已经发到您设置的新邮箱, 请按邮件中的链接验证新邮箱')
