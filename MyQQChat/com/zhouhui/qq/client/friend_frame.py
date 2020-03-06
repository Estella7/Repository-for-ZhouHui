import wx
import threading
import json
import wx.lib.scrolledpanel as scrolled

from com.zhouhui.qq.client.chat_frame import ChatFrame
from com.zhouhui.qq.client.my_frame import *


class FriendFrame(MyFrame):
    def __init__(self,user):
        super().__init__(title = '我的好友',size=(260,600))

        #创建子线程运行状态量
        self.running = True
        #创建线程
        self.t1 = threading.Thread(target=self.thread1_body)

        self.t1.start()

        #聊天窗口初始化
        self.ChatFrame = None
        #用户信息
        self.user = user
        #好友
        self.friends = user['friends']
        #保存好友的控件
        self.friendctrl = []

        #创建顶部面板
        toppanel = wx.Panel(self.fatherpanel)

        # 设置本账号的用户头像,顶部控件
        usericon_file = 'resources/images/{0}.jpg'.format(user['user_icon'])
        usericon = wx.Bitmap(usericon_file, wx.BITMAP_TYPE_JPEG)
        usericon_bitmap = wx.StaticBitmap(self.fatherpanel, bitmap=usericon)
        username_st = wx.StaticText(self.fatherpanel, label='{}'.format(user['user_name']))  # 名字水平居中

        #创建顶部布局
        # 创建一个垂直布局管理器
        hbox_top = wx.BoxSizer()
        hbox_top.AddSpacer(15)
        hbox_top.Add(usericon_bitmap,1,wx.CENTER | wx.EXPAND | wx.ALL,border = 10)
        hbox_top.AddSpacer(15)
        hbox_top.Add(username_st,1,wx.CENTER | wx.EXPAND |wx.ALL,border = 10)
        hbox_top.AddSpacer(15)

        toppanel.SetSizer(hbox_top)

        # 设置好友列表面板为滚动面板,父面板
        friendpanel = scrolled.ScrolledPanel(self.fatherpanel, -1, size=(160, 1000), style=wx.DOUBLE_BORDER)  # 属性是设置一个双层的边框

        gridsizer = wx.GridSizer(20, 1, 1, 1)
        if len(self.friends) > 20:
            gridsizer = wx.GridSizer(rows=len(self.friends), cols=1, gap=(1, 1))

        # 将好友添加进好友列表，使用enumerate函数主要是获取friend表中每一项的索引，用以建立每一个好友的panel
        for index, friend in enumerate(self.friends):
            # 根据获取的索引建立好友面板，子面板
            panel_friend = wx.Panel(friendpanel, id=index)

            # 设置好友的名字和账号显示
            friend_name = wx.StaticText(panel_friend, id=index, style=wx.ALIGN_CENTER_HORIZONTAL,
                                        label=friend['user_name'])
            friend_id = wx.StaticText(panel_friend, id=index, style=wx.ALIGN_CENTER_HORIZONTAL, label=friend['user_id'])

            # 设置好友的头像显示 resources/images/13.JPG
            icon_path = 'resources/images/{0}.jpg'.format(friend['user_icon'])
            friend_iconfile = wx.Bitmap(icon_path, wx.BITMAP_TYPE_JPEG)

            # 假如好友在线，则显示彩图，不在线则显示灰图,0则不可用
            if friend['online'] == '0':
                # 转换为灰色图标
                friend_iconfile2 = friend_iconfile.ConvertToDisabled()
                friend_icon = wx.StaticBitmap(panel_friend, id=index, bitmap=friend_iconfile2, style=wx.BORDER_RAISED)
                friend_icon.Enable(False)
                friend_id.Enable(False)
                friend_name.Enable(False)
                # 保存好友列表
                self.friendctrl.append((friend_name, friend_id, friend_icon, friend_iconfile))
            else:
                friend_icon = wx.StaticBitmap(panel_friend, id=index, bitmap=friend_iconfile, style=wx.BORDER_RAISED)
                friend_icon.Enable(True)
                friend_id.Enable(True)
                friend_name.Enable(True)
                self.friendctrl.append((friend_name, friend_id, friend_icon, friend_iconfile))

            # 为控件绑定双击事件
            friend_icon.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)
            friend_id.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)
            friend_name.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)

            # 创建水平布局，将好友的信息添加进去
            friend_box = wx.BoxSizer()
            friend_box.Add(friend_icon, 1, wx.CENTER)
            friend_box.Add(friend_id, 1, wx.CENTER)
            friend_box.Add(friend_name, 1, wx.CENTER)

            # 将好友的信息添加到根据索引创建的单个好友面板中
            panel_friend.SetSizer(friend_box)
            # 再将单个好友panel添加到整个grid布局中
            gridsizer.Add(panel_friend, 1, wx.ALL, border=5)

            # 将循环之后创建完成的好友列表添加到friendpanel中
        friendpanel.SetSizer(gridsizer)

        #创建垂直布局
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(toppanel,1,wx.EXPAND | wx.CENTER)
        vbox.Add(friendpanel,1,wx.EXPAND | wx.CENTER)

        self.fatherpanel.SetSizer(vbox)


    def OnClick(self,event):
        fid = event.GetId()

        if self.ChatFrame is not None and self.ChatFrame.IsShown():
            dlg = wx.MessageDialog(self,'聊天窗口已打开',
                                   '操作失败',
                                   wx.OK | wx.ICON_ERROR)

            dlg.ShowModal()
            dlg.Destroy()
            return

        self.running = False
        self.t1.join()

        self.ChatFrame = ChatFrame(self,self.user,self.friends[fid])
        self.ChatFrame.Show()

        event.Skip()

    def RefreshFriendList(self, onlineuserlist):
        for index, friend in enumerate(self.friends):
            friendid = friend['user_id']
            # 根据好友列表的索引取出好友的名字，ID，头像等信息
            friend_name, friend_id, friend_icon, friend_iconfile2 = self.friendctrl[index]

            if friendid in onlineuserlist:
                friend_name.Enable(True)
                friend_id.Enable(True)
                friend_icon.Enable(True)
                friend_icon.SetBitmap(friend_iconfile2)
            else:
                friend_name.Enable(False)
                friend_id.Enable(False)
                friend_icon.Enable(False)
                friend_icon.SetBitmap(friend_iconfile2.ConvertToDisabled())

        # 重绘窗口
        self.fatherpanel.Layout()

    def thread1_body(self):
        while self.running:
            try:
                # 从服务器端接收数据
                json_data, _ = client_socket.recvfrom(1024)

                # 对数据进行解码
                json_obj = json.loads(json_data.decode())
                logger.info('从服务器端接收数据：{0}'.format(json_obj))

                # 提取json_data中的command的值
                command = json_obj['command']

                if command is not None and command == COMMAND_REFRESH:
                    user_list = json_obj['OnlineUserList']
                    if user_list is not None and len(user_list) > 0:
                        self.RefreshFriendList(user_list)
            except Exception:
                continue


    def resetthread(self):
        # 重启子线程
        self.running = True
        # 创建一个新的子线程，新线程和原有子线程一样，调用相当于重启
        self.t1 = threading.Thread(target=self.thread1_body())
        self.t1.start()


    def OnClose(self,event):
        if self.ChatFrame is not None and self.ChatFrame.IsShown():
            dlg = wx.MessageDialog(self,'请先关闭聊天窗口，在关闭好友列表','操作失败',wx.OK | wx.ICON_ERROR)

            dlg.ShowModal()
            dlg.Destroy()
            return

        #当前用户下线数据包
        json_obj = {}
        json_obj['command'] = COMMAND_LOGOUT
        json_obj['user_id'] = self.user['user_id']

        #编码
        json_str = json.dumps(json_obj)
        client_socket.sendto(json_str.encode(),sever_address)

        #停止当前子线程
        self.running = False
        self.t1.join()
        self.t1 = None

        #关闭窗口
        super().OnClose(event)