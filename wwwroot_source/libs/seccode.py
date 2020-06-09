#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cStringIO
import Image
import ImageDraw
import ImageFont
import os
import random
import math
import web
from libs import utils

class Seccode:
    def GET(self):
        web.header('Content-Type','image/png')
        web.header('Transfer-Encoding','chunked')
        width = 150
        height = 40
        bgcolor = (255,255,255)
        
        image = Image.new('RGB',(width,height),bgcolor)
        textrand = ''.join(random.sample(('ABCDEFGHIJKLMNPRSTUVWXYZ'),4))
        web.ctx.session.seccode = textrand
        font = ImageFont.truetype(utils.realpath('static/seccode/font/georgia.ttf'),40)
        fontcolor = (0,0,0)
        draw = ImageDraw.Draw(image)
        draw.text((0,0), textrand, font=font, fill=fontcolor)
        del draw
        
        pix = image.load()
        newImage = Image.new('RGB',(width+10,height+30),bgcolor)
        newPix = newImage.load()
        x1 = random.randint(-10,10)
        x2 = random.randint(7,12)
        x3 = random.randint(5,8)
        x4 = random.sample((1,-1),1)[0]
        y1 = random.randint(-3,3)
        y2 = random.randint(9,14)
        y3 = random.randint(7,10)
        y4 = random.sample((1,-1),1)[0]
        for y in xrange(0,height):
            for x in xrange(0,width):
                newx = x + 20 + x1 + math.sin(float(y)/x2)*x3*x4
                newy = y + 13 + y1 + math.sin(float(newx)/y2)*y3*y4
                if newx < width:
                    newPix[newx,newy] = pix[x,y]
        mstream=cStringIO.StringIO()
        newImage.save(mstream, format='png')
        return mstream.getvalue()

class Seccodecheck:
    def GET(self, seccode):
        if seccode.upper() == web.ctx.session.seccode.upper():
            return '<img src=/static/img/check_right.gif height=13 width=13 >'
        else:
            return '<img src=/static/img/check_error.gif height=13 width=13 > ' + u'您输入的验证码不正确，无法提交，请返回修改。'













