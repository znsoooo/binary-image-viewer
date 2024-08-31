import wx


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.bmp = wx.StaticBitmap(self)

        self.path = wx.TextCtrl(self, size=(600, -1))
        self.offset   = wx.SpinCtrl(self, -1, '0', max=wx.INT32_MAX, size=(80, -1))
        self.width    = wx.SpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.height   = wx.SpinCtrl(self, -1, '256', min=1, max=wx.INT32_MAX, size=(80, -1))
        self.channels = wx.SpinCtrl(self, -1, '1', min=1, max=4, size=(80, -1))

        border = 4

        def AddLabel(sizer, label, border):
            sizer.Add(wx.StaticText(self, -1, label), 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border)

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        AddLabel(box1, 'Offset:', border)
        box1.Add(self.offset)
        AddLabel(box1, 'Width:', border)
        box1.Add(self.width)
        AddLabel(box1, 'Height:', border)
        box1.Add(self.height)
        AddLabel(box1, 'Channels:', border)
        box1.Add(self.channels)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.bmp,  1, wx.ALL | wx.ALIGN_CENTER, border)
        box.Add(box1,      0, wx.ALL | wx.ALIGN_CENTER, border)
        box.Add(self.path, 0, wx.ALL | wx.ALIGN_CENTER, border)

        self.SetSizer(box)

    def OnOpen(self, evt):
        dlg = wx.FileDialog(
                self, 'Open file', wildcard='Binary file (*.bin)|*.bin',
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.path.SetValue(dlg.GetPath())
            self.ViewImage()

    def OnSave(self, evt):
        dlg = wx.FileDialog(
                self, 'Save file', wildcard='Binary file (*.bin)|*.bin',
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            print(path)

    def OnPrev(self, evt):
        print('Show prev image')

    def OnNext(self, evt):
        print('Show next image')

    def ViewImage(self):
        path = self.path.GetValue()
        offset = int(self.offset.GetValue())
        width = int(self.width.GetValue())
        height = int(self.height.GetValue())
        channels = int(self.channels.GetValue())

        print((path, offset, width, height, channels))


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Binary Image Viewer', size=(800, 600))
        self.panel = MyPanel(self)
        self.CreateMenu()
        self.Center()
        self.Show()

    def CreateMenu(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()

        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl-O', ' Open a file')
        save_item = file_menu.Append(wx.ID_SAVE, '&Save As\tCtrl-S', ' Save file as')
        file_menu.AppendSeparator()
        prev_item = file_menu.Append(-1, '&Prev Image\tPage Up', ' Show previous image')
        next_item = file_menu.Append(-1, '&Next Image\tPage Down', ' Show next image')
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, 'E&xit\tEsc', ' Exit')

        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.panel.OnOpen, open_item)
        self.Bind(wx.EVT_MENU, self.panel.OnSave, save_item)
        self.Bind(wx.EVT_MENU, self.panel.OnPrev, prev_item)
        self.Bind(wx.EVT_MENU, self.panel.OnNext, next_item)
        self.Bind(wx.EVT_MENU, self.OnClose, exit_item)

    def OnClose(self, evt):
        self.Close()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
