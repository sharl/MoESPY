import os
import sys
import json
import threading
import time

import wx
from wx.adv import TaskBarIcon as TaskBarIcon
import requests

TRAY_ICON = 'icon.png'


def path(r):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, r)


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, frame):
        TaskBarIcon.__init__(self)
        self.message = ''
        self.frame = frame
        self.SetIcon(wx.Icon(path(TRAY_ICON), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=1)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Exit')
        return menu

    def UpdateMessage(self, message):
        self.message = message
        self.SetIcon(wx.Icon(path(TRAY_ICON), wx.BITMAP_TYPE_PNG), self.message)

    def OnTaskBarClose(self, event):
        self.frame.Close()

    def OnTaskBarActivate(self, event):
        if not self.frame.IsShown():
            self.frame.Show()

    def OnTaskBarDeactivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, (-1, -1), (290, 280))
        self.SetIcon(wx.Icon(path(TRAY_ICON), wx.BITMAP_TYPE_PNG))
        self.SetSize((350, 250))
        self.tskic = MyTaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Centre()

    def OnClose(self, event):
        self.tskic.Destroy()
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, -1, __file__)
        self.frame.Show(False)
        self.SetTopWindow(self.frame)
        return True


class Info:
    def __init__(self, app):
        self.app = app
        self.message = ''

    def update(self):
        while True:
            r = requests.get('https://moestats.herokuapp.com/stats', timeout=20)
            if r.status_code in [200, 304]:
                if r.content:
                    j = json.loads(r.content)
                    m = ''
                    for s in j:
                        m += '{} {}\n'.format(s['name'][0], s['login'])
                    self.message = m
                    self.app.frame.tskic.UpdateMessage(m)
            time.sleep(10)

    def run(self):
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()


if __name__ == '__main__':
    app = MyApp(0)
    info = Info(app)
    info.run()
    app.MainLoop()
