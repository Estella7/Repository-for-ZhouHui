import wx
import webbrowser
import json

from com.zhouhui.qq.client.chat_frame import ChatFrame
from com.zhouhui.qq.client.friend_frame import FriendFrame
from com.zhouhui.qq.client.my_frame import *


class LoginFrame(MyFrame):
    def __init__(self):
        super().__init__(title = 'Login...',size = (400,380))

        #创建顶部图片
        topimagefile = wx.Bitmap('resources\images\qq_image.png',wx.BITMAP_TYPE_PNG)
        topimage = wx.StaticBitmap(self.fatherpanel,bitmap = topimagefile)



        #创建一个显示图片的窗口
        image_path = 'resources\images\\1.jpg'
        image = wx.Bitmap(image_path,wx.BITMAP_TYPE_ANY)
        image_head = wx.StaticBitmap(self.fatherpanel,bitmap = image,name = 'image_head')#给一个名字，方便后面代码查询调用

        #创建账号密码输入框
        self.account_txt = wx.TextCtrl(self.fatherpanel)
        self.password_txt = wx.TextCtrl(self.fatherpanel,style = wx.TE_PASSWORD)#限制输入的只能是符合密码的字符

        #设置按钮
        btn_append = wx.Button(self.fatherpanel,label = '注册账号')
        btn_forget = wx.Button(self.fatherpanel,label = '忘记密码')
        btn_append.Bind(wx.EVT_BUTTON,self.OnAppend)
        btn_forget.Bind(wx.EVT_BUTTON,self.OnForget)

        #设置勾选框
        check_rember = wx.CheckBox(self.fatherpanel,-1,'记住密码')
        check_autologin = wx.CheckBox(self.fatherpanel,-1,'自动登录')

        # 创建一个水平布局管理器,中间部分的父管理器,放头像图片和vbox_middle
        hbox = wx.BoxSizer()
        # FlexGrid布局管理器，放输入框和注册账号以及找回密码
        flexgrid_middle = wx.FlexGridSizer(3, 2, 5, 5)

        #将输入框和按钮添加到flexgrid管理器
        flexgrid_middle.AddMany([(self.account_txt,1,wx.EXPAND | wx.CENTER),(btn_append,1,wx.CENTER),
                                 (self.password_txt,1,wx.EXPAND | wx.CENTER),(btn_forget,1,wx.CENTER),
                                 check_rember,check_autologin])

        flexgrid_middle.AddGrowableCol(0,2)
        flexgrid_middle.AddGrowableCol(1,1)
        flexgrid_middle.AddGrowableRow(0,2)
        flexgrid_middle.AddGrowableRow(1,2)
        flexgrid_middle.AddGrowableRow(2,1)

        #将图片显示和右侧的垂直布局管理器加入到中间整个水平管理器
        hbox.Add(image_head,1,flag = wx.EXPAND | wx.CENTER | wx.ALL,border = 5)
        hbox.Add(flexgrid_middle,3,flag = wx.CENTER | wx.ALL,border = 10)

        #设置底部登录按钮
        btn_ok = wx.Button(self.fatherpanel,label = '登录')
        self.Bind(wx.EVT_BUTTON,self.OnClick,btn_ok)

        #创建一个垂直布局管理器，将tim图片，中间部分以及登录按钮添加进面板
        vbox_panel = wx.BoxSizer(wx.VERTICAL)
        vbox_panel.Add(topimage,6,wx.EXPAND)
        vbox_panel.Add(hbox,4,wx.EXPAND | wx.CENTER | wx.ALL,border = 5)
        vbox_panel.Add(btn_ok,1,wx.CENTER | wx.ALL,border = 10)

        self.fatherpanel.SetSizer(vbox_panel)



    def OnClick(self,event):
        account = self.account_txt.GetValue()
        password = self.password_txt.GetValue()
        user = self.login(account,password)

        if user is not None:
            logger.info('登陆成功')
            next_frame = FriendFrame(user)
            next_frame.Show()
            self.Hide()
        else:
            logger.info('登录失败')
            dlg = wx.MessageDialog(self,'您的账号或密码不正确','登陆失败',wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def OnAppend(self,event):
        webbrowser.open('https://ssl.zc.qq.com')

    def OnForget(self,event):
        webbrowser.open('https://aq.qq.com')

    def login(self,userid,password):
        json_obj = {}
        json_obj['command'] = COMMAND_LOGIN
        json_obj['user_id'] = userid
        json_obj['user_password'] = password

        #json编码
        json_str = json.dumps(json_obj)
        #给服务器发送数据,  参数说明：要发送的数据，服务器地址
        client_socket.sendto(json_str.encode(),sever_address)

        #从服务器获取数据,只需要数据，不需要地址，所以地址用'_'代替表示不需要
        json_data,_ = client_socket.recvfrom(1024)
        #对获取的数据进行解码
        json_obj = json.loads(json_data.decode())

        logger.info('从服务器接收数据：{0}'.format(json_obj))

        if json_obj['result'] == '0':
            return json_obj