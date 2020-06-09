#!/usr/bin/python
# -*- coding: UTF-8 -*-

from datetime import datetime
import hashlib
import Image
import os
import re
import random
import threading
import time
import web
import conf

def authcode(text, key, operation='ENCODE'):
    l = list()
    j = 0
    for i in xrange(len(text)):
        j = 0 if j == len(key) - 1 else j + 1
        if operation == 'ENCODE':
            ords = ord(text[i]) + ord(key[j])
        else:
            ords = ord(text[i]) - ord(key[j])
        chars = unichr(ords)
        l.append(chars)
    str_ = ''.join(l)
    if operation == 'ENCODE':
        str_ = str_.replace('\\','\\\\')
        str_ = str_.replace('"','\"')
    return str_

def authkey():
    key = web.cookies().get('key')
    if not key:
        key = str(random.randint(999,999999))
        web.setcookie('key', key)
    return key

def delFiles(paths):
    li = []
    def VisitDir(arg, dirname, names):
        for filepath in names:
            li.append(os.path.join(dirname, filepath))
    os.path.walk(paths, VisitDir, ())
    li.reverse()
    for l in li:
        if os.path.isfile(l):
            os.remove(l)
        else:
            os.rmdir(l)

def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def getimgsize(im, maxwidth, maxheight):
    maxwidth, maxheight = map(float, (maxwidth, maxheight))
    im = Image.open(im)
    imwidth, imheight = map(float, im.size)
    if imwidth > maxwidth or imheight > maxheight:
        if imwidth/maxwidth > imheight/maxheight:
            imheight = maxwidth * imheight / imwidth
            imwidth = maxwidth
        else:
            imwidth = maxheight * imwidth / imheight
            imheight = maxheight
    return imwidth, imheight

def handle_app_urls(path, urls):
    urls = list(urls)
    path = os.path.dirname(os.path.abspath(path))
    path = path.replace(conf.SITE_ROOT, '')
    path = path[1:]
    path = path.replace('\\', '.')
    path = path + '.'
    for i, v in enumerate(urls):
        if i%2 == 1:
            urls[i] = path + v
    urls = tuple(urls)
    return urls

def ip_or_name(name):
    if name and name[0] in ('1','2','3','4','5','6','7','8','9','0'):
        name = ip_safe(name)
    return name

def ip_safe(ip):
    return ip.rsplit('.',1)[0] + '.*'

def multi(page, pagecount, prefix='/'):
    length = 9
    middle = 5
    start = min(max(1, page-middle), max(1, pagecount-length))
    end = min(pagecount, start+length)
    str_ = ''
    if page > 1:
        str_ += '<a href='+prefix+u' >首页</a><a href='+prefix+str(page-1)+u'/ >上一页</a>'
    for pagenum in xrange(start, end+1):
        if pagenum == page:
            str_ += '<span>' + str(pagenum) + '</span>'
        else:
            str_ += '<a href=' + prefix + str(pagenum) + '/ >' + str(pagenum) + '</a>'
    if page < pagecount:
        str_ += '<a href='+prefix+str(page+1)+u'/ >下一页</a><a href='+prefix+str(pagecount)+u'/ >尾页</a>'
    if pagecount == 1:
        str_ = ''
    return str_

def myfiledir(uid, cdir, ac):
    uid = '%012d'%uid
    dir1 = uid[0:3]
    dir2 = uid[3:6]
    dir3 = uid[6:9]
    dir4 = uid[9:]
    filedir = realpath('sitedata/upload', cdir, dir1, dir2, dir3, dir4, ac)
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    return filedir

def get_referer():
    referer = web.ctx.env.get('HTTP_REFERER', '/').split(web.ctx.env.get('HTTP_HOST'))
    referer = referer[1] if len(referer)>1 else referer[0]
    if not re.match(r'''(\/post[\/\d]*|\/chat/)''', referer, re.I|re.S):
        referer = '/'
    return referer

def htmlquote(txt):
    return web.net.htmlquote(txt).replace('\r\n', '<br>').replace('\n', '<br>').replace(' ', '&nbsp;')

def realpath(*args):
    return os.path.join(conf.SITE_ROOT, *args)

def redirect(url, **kwargs):
    url = url.split('?rand=')[0]
    url = url+'?rand='+str(time.time()).replace('.','')+str(random.randint(100000,999999))
    delay = kwargs.pop('delay', 0)
    msg = kwargs.pop('msg', '')
    if msg != '':
        msg = u'<div style="width:100%%; margin-top:200px; text-align:center; font-size:14px; font-weight:bold;">%s，将在%s秒钟后转向目标页面</div>' % (msg, delay)
    html = '''
           <html>
           <head>
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
           <meta http-equiv="refresh" content="%s;url=%s">
           </head>
           <body>
           %s
           </body>
           </html>
           ''' % (delay, url, msg)
    return html

def sha1(str_):
    return hashlib.sha1(str_).hexdigest()    

class ThreadSkeleton(threading.Thread):
    def __init__(self, func, **kwargs):
        threading.Thread.__init__(self)
        self.func = func
        self.kwargs = kwargs
    def run(self):
        self.func(**self.kwargs)
