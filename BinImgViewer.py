import os
import re
import sys
import math
import itertools
import traceback

import wx

osp = os.path


__title__ = 'Binary Image Viewer'


def protect(fn):
    def wrapper(*v, **kv):
        try:
            return fn(*v, **kv)
        except Exception:
            traceback.print_exc()
            msg = traceback.format_exc(-1)
            wx.MessageBox(msg)
    return wrapper


def ChainBytes(iter):
    return bytes(itertools.chain.from_iterable(iter))


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, callback):
        wx.FileDropTarget.__init__(self)
        self.callback = callback

    def OnDropFiles(self, x, y, filenames):
        self.callback(filenames[0])
        return False


class MySpinCtrl(wx.SpinCtrl):
    def __init__(self, *args, **kw):
        wx.SpinCtrl.__init__(self, *args, **kw)
        self.Bind(wx.EVT_SPINCTRL, lambda e: self.SetInsertionPointEnd())

    def SetInsertionPointEnd(self):
        self.SetSelection(-2, -1)

    def SetValue(self, value):
        super().SetValue(value)
        self.SetInsertionPointEnd()


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.bmp = wx.StaticBitmap(self)

        self.last_path = None
        self.last_data = None
        self.last_img  = None
        self.last_channels = 3

        self.path     = wx.TextCtrl(self)
        self.width    = MySpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.height   = MySpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.channels = MySpinCtrl(self, -1, str(self.last_channels), min=1, max=4, size=(80, -1))

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

    def GetPath(self):
        return osp.abspath(self.path.GetValue().strip('\'"'))

    def OnOpen(self, evt):
        dlg = wx.FileDialog(self, 'Open file',
            wildcard='Image file|*.bin;*.png;*.jpg;*.jpeg;*.bmp;*.gif|All file|*.*',
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetPath(dlg.GetPath())
            self.ViewImage(None)

    def OnSave(self, evt):
        if not self.bmp.GetBitmap():
            return
        path = self.GetPath()
        dlg = wx.FileDialog(self, 'Save file',
            defaultDir=osp.dirname(path),
            defaultFile=osp.splitext(osp.basename(path))[0],
            wildcard='Binary file|*.bin|Image file|*.png',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.SaveImage(path)

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

    def SetPath(self, path):
        self.path.SetValue(path)
        self.path.SetInsertionPointEnd()

    @protect
    def SaveImage(self, path):
        img = self.bmp.GetBitmap().ConvertToImage()
        if re.search(r'\.png$', path, re.I):
            img.SaveFile(path, wx.BITMAP_TYPE_PNG)
        else:
            channels = self.channels.GetValue()
            data = img.GetData()
            if channels == 1:
                data = bytes(data[i] for i in range(0, len(data), 3))
            elif channels == 4:
                alpha = img.GetAlphaBuffer() or b'\xff' * (len(data) // 3)
                data = ChainBytes([*data[3*i:3*i+3], alpha[i]] for i in range(len(alpha)))
            with open(path, 'wb') as f:
                f.write(data)

    @protect
    def ViewNext(self, next):
        path = self.GetPath()
        root = path if osp.isdir(path) else osp.dirname(path)
        paths = [osp.join(root, name) for name in os.listdir(root) if re.search(r'\.(bin|png|jpe?g|bmp|gif)$', name, re.I)]
        paths = sorted(paths if path in paths else paths + [path])
        if len(paths) > 1:
            idx = paths.index(path)
            idx = (idx + next) % len(paths)
            self.SetPath(paths[idx])

    @protect
    def ViewImage(self, evt):
        path = self.GetPath()
        width = self.width.GetValue()
        height = self.height.GetValue()
        channels = self.channels.GetValue()

        if channels == 2:
            channels = 1 if self.last_channels > 2 else 3
            self.channels.SetValue(channels)
            self.last_channels = channels

        if not os.path.isfile(path):
            self.bmp.SetBitmap(wx.Bitmap())
            self.parent.SetTitle(__title__)
        else:
            if not self.ViewNormalImage(path, channels):
                self.ViewBinImage(path, width, height, channels)
            self.parent.SetTitle(f'{osp.basename(path)} - {__title__}')
        self.last_path = path
        self.Layout()

    @protect
    def ViewNormalImage(self, path, channels):
        with wx.LogNull():
            if path != self.last_path:
                self.last_img = wx.Image(path)
            img = self.last_img
            if not img:
                return False

        if channels == 1:
            img = img.ConvertToGreyscale()
        if channels in [1, 3]:
            img0 = wx.Image(img.GetSize())
            img0.SetRGB(wx.Rect(img.GetSize()), 255, 255, 255)
            img0.Paste(img, 0, 0, wx.IMAGE_ALPHA_BLEND_COMPOSE)
            img = img0
        self.width.SetValue(img.GetWidth())
        self.height.SetValue(img.GetHeight())

        self.bmp.SetBitmap(img.ConvertToBitmap())
        return True

    @protect
    def ViewBinImage(self, path, width, height, channels):
        if path != self.last_path:
            with open(path, 'rb') as f:
                self.last_data = f.read()
        data = self.last_data

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
            data = ChainBytes(zip(data, data, data))
            bmp = bmp.FromBuffer(width, height, data)
        elif channels == 3:
            bmp = bmp.FromBuffer(width, height, data)
        else: # channels == 4:
            bmp = bmp.FromBufferRGBA(width, height, data)
        self.bmp.SetBitmap(bmp)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Binary Image Viewer', size=(800, 600))
        self.panel = MyPanel(self)
        self.CreateMenu()
        self.Center()
        self.Show()

        dt = MyFileDropTarget(self.panel.SetPath)
        self.SetDropTarget(dt)

        if sys.argv[1:]:
            self.panel.SetPath(sys.argv[1])

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
