import os
import sys
import glob
import math
import itertools

import wx

osp = os.path


__title__ = 'Binary Image Viewer'


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, callback):
        wx.FileDropTarget.__init__(self)
        self.callback = callback

    def OnDropFiles(self, x, y, filenames):
        self.callback(filenames[0])
        return False


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.bmp = wx.StaticBitmap(self)

        self.last_path = None
        self.last_data = None
        self.last_channels = 3

        self.path     = wx.TextCtrl(self)
        self.width    = wx.SpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.height   = wx.SpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.channels = wx.SpinCtrl(self, -1, str(self.last_channels), min=1, max=4, size=(80, -1))

        border = 4

        def AddLabel(sizer, label, border):
            sizer.Add(wx.StaticText(self, -1, label), 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border)

        box1 = wx.BoxSizer()
        AddLabel(box1, 'Width:', border)
        box1.Add(self.width)
        AddLabel(box1, 'Height:', border)
        box1.Add(self.height)
        AddLabel(box1, 'Channels:', border)
        box1.Add(self.channels)

        box2 = wx.BoxSizer()
        AddLabel(box2, 'Path:', border)
        box2.Add(self.path, 1, wx.EXPAND)

        box3 = wx.BoxSizer(wx.VERTICAL)
        box3.Add(box1, 1, wx.ALL | wx.EXPAND, border)
        box3.Add(box2, 1, wx.ALL | wx.EXPAND, border)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.bmp, 1, wx.ALL | wx.ALIGN_CENTER, 0)
        box.Add(box3,     0, wx.ALL | wx.ALIGN_CENTER, border)

        self.SetSizer(box)

        self.path.Bind(wx.EVT_TEXT, self.ViewImage)
        self.width.Bind(wx.EVT_TEXT, self.ViewImage)
        self.height.Bind(wx.EVT_TEXT, self.ViewImage)
        self.channels.Bind(wx.EVT_TEXT, self.ViewImage)

        self.path.Bind(wx.EVT_KEY_DOWN, self.OnPathKeyDown)
        self.path.Bind(wx.EVT_MOUSEWHEEL, self.OnPathWheelDown)

    def OnOpen(self, evt):
        dlg = wx.FileDialog(
                self, 'Open file', wildcard='Binary file (*.bin)|*.bin|All file (*.*)|*.*',
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.path.SetValue(dlg.GetPath())
            self.ViewImage(None)

    def OnSave(self, evt):
        dlg = wx.FileDialog(
                self, 'Save file', wildcard='Binary file (*.bin)|*.bin|All file (*.*)|*.*',
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            wx.MessageBox('Unfilled.')

    def OnPathKeyDown(self, evt):
        code = evt.GetKeyCode()
        if code == wx.WXK_DOWN:
            self.ViewNext(1)
        elif code == wx.WXK_UP:
            self.ViewNext(-1)
        else:
            evt.Skip()

    def OnPathWheelDown(self, evt):
        if evt.GetWheelRotation() < 0:
            self.ViewNext(1)
        else:
            self.ViewNext(-1)

    def ViewNext(self, next):
        path = osp.abspath(self.path.GetValue().strip('\'"'))
        root = path if osp.isdir(path) else osp.dirname(path)
        paths = glob.glob(osp.join(root, '*.bin'))
        if paths:
            idx = paths.index(path) if path in paths else 0
            idx = (idx + next) % max(len(paths), 1)
            self.path.SetValue(paths[idx])
            self.path.SetInsertionPointEnd()

    def ViewImage(self, evt):
        path = osp.abspath(self.path.GetValue().strip('\'"'))
        width = int(self.width.GetValue())
        height = int(self.height.GetValue())
        channels = int(self.channels.GetValue())

        if channels == 2:
            channels = 1 if self.last_channels > 2 else 3
            self.channels.SetValue(str(channels))
            self.last_channels = channels

        if path == self.last_path:
            data = self.last_data
        else:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                self.last_data = data
                self.last_path = path
            except Exception:
                self.bmp.SetBitmap(wx.Bitmap())
                self.parent.SetTitle(__title__)
                return

        data_size = len(data)
        if data_size != width * height * channels:
            if self.height.HasFocus():
                width = math.ceil(data_size / height / channels)
                self.width.SetValue(width)
            else:
                height = math.ceil(data_size / width / channels)
                self.height.SetValue(height)
            diff_size = width * height * channels - data_size
            data = data + b'\0' * diff_size

        bmp = wx.Bitmap()
        if max(width, height) > 10000:
            pass  # Too large image size make program crash
        elif channels == 1:
            data = bytes(itertools.chain.from_iterable(zip(data, data, data)))
            bmp = bmp.FromBuffer(width, height, data)
        elif channels == 3:
            bmp = bmp.FromBuffer(width, height, data)
        else: # channels == 4:
            bmp = bmp.FromBufferRGBA(width, height, data)
        self.bmp.SetBitmap(bmp)

        self.Layout()
        self.parent.SetTitle(f'{osp.basename(path)} - {__title__}')


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Binary Image Viewer', size=(800, 600))
        self.panel = MyPanel(self)
        self.CreateMenu()
        self.Center()
        self.Show()

        dt = MyFileDropTarget(self.panel.path.SetValue)
        self.SetDropTarget(dt)

        if sys.argv[1:]:
            self.panel.path.SetValue(sys.argv[1])

    def CreateMenu(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()

        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl-O', ' Open a file')
        save_item = file_menu.Append(wx.ID_SAVE, '&Save\tCtrl-S', ' Save file as')
        file_menu.AppendSeparator()
        prev_item = file_menu.Append(-1, '&Prev\tPgUp', ' Show previous image')
        next_item = file_menu.Append(-1, '&Next\tPgDn', ' Show next image')
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, 'E&xit\tEsc', ' Exit')

        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.panel.OnOpen, open_item)
        self.Bind(wx.EVT_MENU, self.panel.OnSave, save_item)
        self.Bind(wx.EVT_MENU, lambda e: self.panel.ViewNext(-1), prev_item)
        self.Bind(wx.EVT_MENU, lambda e: self.panel.ViewNext( 1), next_item)
        self.Bind(wx.EVT_MENU, self.OnClose, exit_item)

    def OnClose(self, evt):
        self.Close()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
