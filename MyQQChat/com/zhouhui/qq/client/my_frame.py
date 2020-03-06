import logging
import socket
import sys
import wx

logger = logging.getLogger(__name__)
#服务器IP
SERVER_IP = '127.0.0.1'
#服务器端口号
SERVER_PORT = 8888
#服务器地址
sever_address = (SERVER_IP,SERVER_PORT)

#操作命令代码
COMMAND_LOGIN = 1
COMMAND_LOGOUT = 2
COMMAND_SENDMSG = 3
COMMAND_REFRESH = 4

#创建一个基于udp的对象
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

client_socket.settimeout(1)


class MyFrame(wx.Frame):
    def __init__(self,size,title):
        super().__init__(parent = None,title = title ,size = size,style = wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX)#异或方法可以去除不需要的样式

        # 居中
        self.Center()

        self.fatherpanel = wx.Panel(self)

        # 设置窗口图标
        ico = wx.Icon('resources\icon\qq.ico',wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        #设置窗口的尺寸大小，不可缩放
        self.SetSizeHints(size,size)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def OnClose(self,event):
        #退出系统
        self.Destroy()
        client_socket.close()
        sys.exit(0)