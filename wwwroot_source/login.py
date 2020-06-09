#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import time
from time import time as now
import web
import apps
import conf
from conn import db
from libs.common import *
from libs import utils
from moduls.moduls import User

def setcookie_login(uid):
    u = User(uid=uid,
    )
    user = u.get()
    uid, lastlogintime, salt = str(user[0].uid), int(now()), str(user[0].salt)
    uid_secret = uid+'_'+utils.sha1(utils.sha1(uid)+utils.sha1(str(lastlogintime))+utils.sha1(salt)+utils.sha1(conf.cookies_secret_key))
    web.setcookie('uid', uid_secret, 86400*30)

    u.update(lastloginip=web.ctx.ip, lastlogintime=lastlogintime)

class Activate:
    def GET(self, uid, acstr):
        setting = web.config._setting
        my = web.Storage()
        my.uid = uid

        u = User(uid=uid,
        )
        user = u.get()
        if len(user) == 0:
            my.uid = 0
            return showmsg(u'不存在改用户')
        else:
            my.update(user[0])
            my.update(u.getfields()[0])
            del my.password, my.salt
            if my.activate == '':
                return utils.redirect('/')
            my.actime, my.acstr = my.activate.split('|')
            if int(now()) - int(my.actime) > 86400 * 7:
                my.uid = 0
                return showmsg(u'验证链接已过期')
            elif my.acstr != acstr.strip('/'):
                my.uid = 0
                return showmsg(u'验证链接错误')
            elif User().existemail2(my.uid, my.email):
                return showmsg(u'邮箱已被别人使用, 请 <a href="/profiles/email/">更换一个新的邮箱</a>')
            else:
                u.update(groupid=2)
                u.updatefields(activate='0|0')
                setcookie_login(my.uid)
                msg = u'验证成功，'

                d=locals();d.pop('self')
                return utils.redirect('/', delay=3, msg=msg)

class Acemail:
    def GET(self, uid, email, acstr):
        setting = web.config._setting
        my = web.Storage()
        my.uid = uid

        u = User(uid=uid,
        )
        user = u.get()
        if len(user) == 0:
            my.uid = 0
            return showmsg(u'不存在该用户', redirect = '/')
        else:
            my.update(user[0])
            my.update(u.getfields()[0])
            del my.password, my.salt
            my.actime, my.acstr = my.activate.split('|')
            if int(now()) - int(my.actime) > 86400 * 7:
                my.uid = 0
                return showmsg(u'验证连接已过期')
            elif my.acstr != acstr.split('|')[1].strip('/'):
                my.uid = 0
                return showmsg(u'验证链接错误')
            elif User().existemail2(my.uid, my.email):
                return showmsg(u'邮箱已被别人使用, 请 <a href="/profiles/email/">更换一个新的邮箱</a>')
            else:
                u.update(email=email, groupid=2)
                u.updatefields(activate='0|0')
                setcookie_login(my.uid)
                msg = u'新邮箱验证成功，'

                d=locals();d.pop('self')
                return utils.redirect('/', delay=3, msg=msg)

class Login:
    @check_login()
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        if my.uid != 0: return utils.redirect('/')

        web.setcookie('referer', utils.get_referer())

        d=locals();d.pop('self')
        return conf.render.login(**d)

    @check_login()
    def POST(self):
        setting = web.config._setting
        my = self.POST.my
        if my.uid != 0: return utils.redirect('/')

        post = web.input()
        u = User(username=post.username,
        )
        user = u.get()
        if len(user) == 0:
            return showmsg(u'不存在该用户', referer = 'back')
        elif user[0].password == utils.sha1(utils.sha1(post.password)+str(user[0].salt)):
            setcookie_login(user[0].uid)

            referer = web.cookies(referer='/').referer
            if '/login' in referer: referer = '/'
            web.setcookie('referer', '', 0)
            return utils.redirect(referer)
        else:
            return showmsg(u'密码错误', referer = 'back')

class Logout:
    def GET(self):
        web.setcookie('uid', '0_0')
        referer = utils.get_referer()
        return utils.redirect(referer)

class Losspass:
    @check_login()
    def GET(self):
        setting = web.config._setting
        my = self.GET.my

        if setting.reg_email != 'on':
            return showmsg('email is closed')

        d=locals();d.pop('self')
        return conf.render.losspass(**d)
    def POST(self):
        setting = web.config._setting
        if setting.reg_email != 'on':
            return showmsg('email is closed')
        post = web.input()
        if post.seccode.upper() != web.ctx.session.seccode.upper():
            return showmsg(u'验证码错误', referer='back')
        del web.ctx.session.seccode
        u = User(username=post.username,
        )
        user = u.get()
        if len(user) == 0:
            return showmsg(u'不存在该用户', referer='back')
        u.uid = user[0].uid
        if user[0].email != post.email:
            return showmsg(u'用户名跟Email不匹配', referer='back')
        elif int(now()) - int(u.getfields()[0].activate.split('|')[0]) < 60 * 15:
            return showmsg(u'刚刚发送了一封邮件到您的Email, 请15分钟后再试', referer='back')
        else:
            activate = str(int(now())) + '|' + ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',20))
            u.updatefields(activate=activate)

            try:
                self.__sendmail(user[0], activate)
            except Exception, e:
                return e

            return showmsg(u'一封新邮件已经发到您的邮箱, 请按邮件中的链接设置新密码')

    def __sendmail(self, user, activate):
        activate = activate.split('|')[1]
        subject = u'找回密码的认证链接'
        message = u'''
        %s，您好：
        请点击下面的链接设置您的新密码：

        http://%s/losspass/setnewpass/%s/%s/

        (如果上面不是链接形式，请将地址手工粘贴到浏览器地址栏再访问)
        ''' % (user.username, web.ctx.env.get('HTTP_HOST'), user.uid, activate)

        web.sendmail(web.config.smtp_username, user.email, subject, message)

class Setnewpass:
    @check_login()
    def GET(self, uid, acstr):
        setting = web.config._setting
        my = self.GET.my

        u = User(uid=uid,
        )
        user = u.get()
        if len(user) == 0:
            return showmsg(u'不存在该用户')
        else:
            u_actime, u_acstr = u.getfields()[0].activate.split('|')
            if int(now()) - int(u_actime) > 86400 * 7:
                return showmsg(u'验证连接已过期')
            elif u_acstr != acstr:
                return showmsg(u'验证链接错误')
            else:
                d = locals();d.pop('self')
                return conf.render.setnewpass(**d)
    def POST(self, uid, acstr):
        u = User(uid=uid,
        )
        user = u.get()
        if len(user) == 0:
            return showmsg(u'不存在该用户')
        else:
            post = web.input()
            u_actime, u_acstr = u.getfields()[0].activate.split('|')
            if int(now()) - int(u_actime) > 86400 * 7:
                return showmsg(u'验证连接已过期')
            elif u_acstr != acstr:
                return showmsg(u'验证链接错误')
            elif post.password != post.password2:
                return showmsg(u'两次输入的密码不一致', referer='back')
            else:
                salt = random.randint(100000,999999)
                password = utils.sha1(utils.sha1(post.password)+str(salt))
                u.update(salt=salt, password=password)
                u.updatefields(activate='0|0')

                return showmsg(u'新密码设置成功，请 <a href="/login/">用新密码登录</a>')


class Register:
    @check_login()
    def GET(self):
        setting = web.config._setting
        my = self.GET.my
        if my.uid != 0: return utils.redirect('/')
        if setting.reg_open != 'on': return showmsg(u'已经关闭注册')

        d=locals();d.pop('self')
        return conf.render.register(**d)

    @check_login()
    def POST(self):
        setting = web.config._setting
        my = self.POST.my
        if my.uid != 0: return utils.redirect('/')
        if setting.reg_open != 'on': return showmsg(u'已经关闭注册')
        post = web.input()
        if len(post.username) < 3:
            return showmsg(u'用户名太短(最少3个字符)', referer='back')
        if len(post.password) < 6:
            return showmsg(u'密码太短(最少6个字符)', referer='back')
        if len(post.email) == 0:
            return showmsg(u'邮箱不能为空', referer='back')
        if post.password != post.password2:
            return showmsg(u'两次输入的密码不一致', referer='back')
        if setting.reg_seccode == 'on':
            if post.seccode.upper() != web.ctx.session.seccode.upper():
                return showmsg(u'验证码错误', referer='back')
            del web.ctx.session.seccode

        u = User()
        u.username = post.username
        u.password = post.password
        if u.getcount() == 0:
            u.groupid = 4
            web.config._setting.usercount = 1
            set_setting()
        elif setting.reg_email == 'on':
            u.groupid = 1
        else:
            u.groupid = 2
        u.email = post.email
        u.gender = post.gender
        if u.existname():
            return showmsg(u'用户名已存在', referer='back')
        if u.existemail() and setting.reg_email == 'on':
            return showmsg(u'Email已经存在', referer='back')
        if setting.reg_invite == 'on':
            I = apps.admin.admin_moduls.Invite(invite=post.invite,
            )
            inv = I.get()
            if len(inv) == 0:
                return showmsg(u'邀请码错误', referer='back')
            elif int(now()) - int(inv[0].createtime) > 86400 * 7:
                return showmsg(u'邀请码已经过期', referer='back')
            elif inv[0].usedtime > 0:
                return showmsg(u'邀请码已被用过', referer='back')
            else:
                I.iid = inv[0].iid
                I.update(username=u.username, usedtime=int(now()))
        u.uid = u.add()

        u.face = 'face/defaultface.gif?v=0|64|64'
        u.sightml = ''
        if setting.reg_email == 'on':
            u.activate = str(int(now())) + '|' + ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',20))
        else:
            u.activate = '0|0'
        u.addfields()

        if setting.reg_email == 'on':
            try:
                self.__sendmail(post, u.uid, u.activate)
            except Exception, e:
                return e

        setcookie_login(u.uid)

        return utils.redirect('/')
    def __sendmail(self, post, uid, activate):
        activate = activate.split('|')[1]
        subject = u'你在%s的注册资料' % web.config._setting.sitename
        message = u'''
        %s，您好：
        欢迎您加入 %s 这个大家庭！您只需点击下面的链接即可激活您的帐号：

        http://%s/register/activate/%s/%s/

        (如果上面不是链接形式，请将地址手工粘贴到浏览器地址栏再访问)

        请记住您的注册信息
        用户名：%s
        密  码：%s
        ''' % (post.username, web.config._setting.sitename, web.ctx.env.get('HTTP_HOST'), uid, activate, post.username, post.password)

        web.sendmail(web.config.smtp_username, post.email, subject, message)