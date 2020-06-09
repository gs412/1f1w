#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import wx
from wx import xrc
import win32event
import pywintypes
import win32api
import random
import ConfigParser
import subprocess
import thread
import time
import re
import urllib2
import webbrowser

global_port = 0

def randport():
    port = random.randint(2,999)
    if port in (7,19,21,22,23,25,31,42,53,67,69,79,80,99,102,109,110,113,119,123,135,137,138,139,143,161,177,389,443,456,513,544,553,555,568,569,635,636,666,993):
        port = randport()
    return str(port)

def getport():
    cfg = ConfigParser.ConfigParser()
    cfg.read("config.ini")
    port = cfg.get("default","port")
    if port == "0":
        port = randport()
        cfg.set("default","port",port)
        f = open("config.ini","r+")
        cfg.write(f)
        f.close()
    return port

def setport(port):
    cfg = ConfigParser.ConfigParser()
    cfg.read("config.ini")
    cfg.set("default","port",port)
    f = open("config.ini","r+")
    cfg.write(f)
    f.close()

def server(do):
    f = file("l_stop.log","w+")
    f.write(do)
    f.close()

def alive():
    while True:
        f = file("l_alive.log","w+")
        f.write("")
        f.close()
        time.sleep(60)

class Getmyip:
    def getip(self):
        try:
            myip = self.visit("http://www.ip138.com/ip2city.asp")
        except:
            try:
                myip = self.visit("http://www.bliao.com/ip.phtml")
            except:
                try:
                    myip = self.visit("http://www.whereismyip.com/")
                except:
                    myip = "So sorry!!!"
        return myip
    def visit(self,url):
        opener = urllib2.urlopen(url)
        if url == opener.geturl():
            str = opener.read()
        return re.search('\d+\.\d+\.\d+\.\d+',str).group(0)

class TaskBarIcon(wx.TaskBarIcon):
    ID_EXIT = wx.NewId()
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='images\\1f1w.ico', type=wx.BITMAP_TYPE_ICO), u"一花一世界")
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnEXIT, id=self.ID_EXIT)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
           self.frame.Iconize(False)
        if not self.frame.IsShown():
           self.frame.Show(True)
        self.frame.Raise()

    def OnEXIT(self, event):
        server("stop")
        self.Destroy()
        thread.exit()

    # override
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_EXIT, u"退出")
        return menu

class MyDialog(wx.Dialog):
    def __init__(self, frame, id, title):
        wx.Dialog.__init__(self, frame, id, title)
        self.frame = frame
        panel = wx.Panel(self)
        wx.StaticText(panel, -1, u"您点击了关闭按钮，您希望:", (40,15), (200,15))
        self.radio = 1
        radio1 = wx.RadioButton(panel, 1, u"最小化到托盘区，不退出", (60,40))
        radio2 = wx.RadioButton(panel, 2, u"停止服务并退出程序", (60,60))
        self.Bind(wx.EVT_RADIOBUTTON, self.SetRadio, radio1)
        self.Bind(wx.EVT_RADIOBUTTON, self.SetRadio, radio2)
        submitBtn = wx.Button(panel, -1, u"确定", pos=(140,110),size=(70,21))
        cancelBtn = wx.Button(panel, -1, u"取消", pos=(215,110),size=(70,21))
        self.Bind(wx.EVT_BUTTON, self.CloseFrame, submitBtn)
        self.Bind(wx.EVT_BUTTON, self.CloseDlg, cancelBtn)

    def SetRadio(self, event):
        radioSelected = event.GetEventObject()
        self.radio = radioSelected.GetId()

    def CloseFrame(self, event):
    	self.Close()
        if self.radio==1:
            self.frame.Hide()
        else:
            server("stop")
            self.frame.Destroy()
            self.frame.taskBarIcon.Destroy()

    def CloseDlg(self, event):
        self.Destroy()



class Frame(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource('resources\Frame.xrc')
        self.init_frame()
        return True
    def init_frame(self):
        self.frame = self.res.LoadFrame(None, 'Frame')
        self.frame.SetIcon(wx.Icon('images\\1f1w.ico', wx.BITMAP_TYPE_ICO))
        self.panel = xrc.XRCCTRL(self.frame, 'panel')
        self.port = xrc.XRCCTRL(self.panel, 'port')
        self.port.SetValue(getport())
        self.start = xrc.XRCCTRL(self.panel, 'start')
        self.start.SetFocus()
        self.stop = xrc.XRCCTRL(self.panel, 'stop')
        self.stop.Enable(False)
        self.restart = xrc.XRCCTRL(self.panel, 'restart')
        self.restart.Enable(False)
        self.status = xrc.XRCCTRL(self.panel, 'status')
        self.urltip = xrc.XRCCTRL(self.panel, 'urltip')
        self.urltip.Hide()
        self.myurl = xrc.XRCCTRL(self.panel, 'myurl')
        self.myurl.Hide()

        self.frame.taskBarIcon = TaskBarIcon(self.frame)
        # bind event
        self.frame.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)
        self.frame.Bind(wx.EVT_ICONIZE, self.OnIconfiy, self.frame)
        self.frame.Bind(wx.EVT_BUTTON, self.Start, self.start)
        self.frame.Bind(wx.EVT_BUTTON, self.Stop, self.stop)
        self.frame.Bind(wx.EVT_BUTTON, self.Restart, self.restart)
        self.panel.Bind(wx.EVT_LEFT_DOWN, lambda x:self.frame.SetFocus())
        self.myurl.Bind(wx.EVT_LEFT_DOWN, lambda x:(self.myurl.SetFocus(),self.myurl.SelectAll()))

        self.frame.Show()
        thread.start_new_thread(alive,())
    def OnHide(self, event):
        self.frame.Hide()
    def OnIconfiy(self, event):
        self.frame.Hide()
    def OnClose(self, event):
        dialog = MyDialog(self.frame, -1, u"关闭设置")
        width = 300
        height = 170
        dialog.SetSize((width, height))
        pos = self.frame.GetPosition()
        size = self.frame.GetSize()
        dialog.SetPosition((pos[0]+((size[0]-width)/2), pos[1]+((size[1]-height)/2)))
        dialog.ShowModal()
    def Start(self, event):
        self.port.Enable(False)
        self.start.Enable(False)
        server("stop")
        self.status.SetLabel(u"正在启动网站，请稍后……")
        wx.FutureCall(1100, self.Start_call, '', '')
    def Start_call(self, *args, **kwargs):
        server("start")
        proc = subprocess.Popen(args="server1f1w.exe "+str(self.port.GetValue())+"", shell=True, stdout=open("l_stdout.log", "w"), stderr=open("l_stdout.log"))
        self.stop.Enable(True)
        self.restart.Enable(True)
        self.status.SetLabel(u"网站运行中")
        wx.FutureCall(10, self.Open_url, '', '')
    def Open_url(self, *args, **kwargs):
        global global_port
        localip = Getmyip().getip()
        if self.port.GetValue() == "80":
            url = "http://" + localip
        else:
            url = "http://" + localip + ":" + self.port.GetValue()
        self.urltip.Show()
        self.myurl.Show()
        self.myurl.Value=url
        if not self.port.GetValue() == global_port:
            webbrowser.open_new(url)
        setport(self.port.GetValue())
        global_port = self.port.GetValue()
    def Stop(self, event):
        self.stop.Enable(False)
        self.restart.Enable(False)
        self.urltip.Hide()
        self.myurl.Hide()
        server("stop")
        self.status.SetLabel(u"正在停止网站，请稍后……")
        wx.FutureCall(1100, self.Stop_call, '', '')
    def Stop_call(self, *args, **kwargs):
        self.port.Enable(True)
        self.start.Enable(True)
        self.urltip.Hide()
        self.myurl.Hide()
        self.status.SetLabel(u"已停止")
    def Restart(self, event):
        self.stop.Enable(False)
        self.restart.Enable(False)
        server("stop")
        self.status.SetLabel(u"正在重启网站，请稍后……")
        wx.FutureCall(1100, self.Start_call, '', '')

class Alert(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource('resources\Dialog_hasrun.xrc')
        self.init_frame()
        return True
    def init_frame(self):
        self.frame = self.res.LoadFrame(None, 'Dialog_hasrun')
        self.frame.SetIcon(wx.Icon('images\\1f1w.ico', wx.BITMAP_TYPE_ICO))
        self.frame.Bind(wx.EVT_BUTTON, self.CloseFrame, id=xrc.XRCID('OkBtn'))
        self.frame.Show()
    def CloseFrame(self, event):
        self.frame.Destroy()


def start():
    RUN_ALREADY_EXISTS = 183
    sz_mutex = "lock_mutex_4_1f1w"
    hmutex = win32event.CreateMutex(None, pywintypes.FALSE,sz_mutex)
    if (win32api.GetLastError() == RUN_ALREADY_EXISTS):
        app = Alert(False)
        app.MainLoop()
    else:
        app = Frame(False)
        app.MainLoop()


if __name__ == '__main__':
    start()