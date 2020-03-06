import wx
import json
import threading
import datetime
from com.zhouhui.qq.client.my_frame import *


class ChatFrame(MyFrame):
    def __init__(self,friendframe,user,friend):
        super().__init__(title='',size=(700,500))

        #子线程运行状态量
        self.running = True
        #创建线程
        self.t1 = threading.Thread(target=self.thread_body)
        #启动线程
        self.t1.start()

        #消息日志
        self.msglog = ''
       #用户信息
        self.user = user
        #好友信息
        self.friend = friend
        #重新定义title的内容
        title = '{0}与{1}聊天中...'.format(user['user_name'], friend['user_name'])
        self.SetTitle(title)

#___________________________________________________________聊 天 窗 口________________________________________________________
        #创建文本框控件，上面部分是一个只读的文本框
        self.seemsg_top = wx.TextCtrl(self.fatherpanel,style = wx.TE_MULTILINE | wx.TE_READONLY)
        #设置文本框中文字的样式
        self.seemsg_top.SetFont(wx.Font(9,wx.FONTFAMILY_DEFAULT,
                                         wx.FONTSTYLE_NORMAL,
                                         wx.FONTWEIGHT_NORMAL,
                                         faceName = '微软雅黑'))

        #创建输入文本框，消息输入框
        self.sendmsg_bottom = wx.TextCtrl(self.fatherpanel)
        #设置焦点，使用SetFoucs函数
        self.sendmsg_bottom.SetFocus()
        #设置字体
        self.sendmsg_bottom.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                             wx.FONTSTYLE_NORMAL,
                                             wx.FONTWEIGHT_NORMAL, faceName='微软雅黑'))

        #创建发送按钮
        btn_ok = wx.Button(self.fatherpanel,label = '发送')
        btn_ok.Bind(wx.EVT_BUTTON,self.OnBtnOk)

        #创建垂直布局,存放seemsg_top和sendmessage_box
        message_box = wx.BoxSizer(wx.VERTICAL)

        #创建水平布局，存放btn_ok和sendmsg_bottom
        sendmessage_box = wx.BoxSizer()

        #将输入框和发送按钮添加进水平布局
        sendmessage_box.Add(self.sendmsg_bottom,3,wx.CENTER | wx.EXPAND)
        sendmessage_box.Add(btn_ok,1,wx.EXPAND | wx.CENTER | wx.ALL,border = 5)

        #将底部布局和顶部显示框加入到整体的垂直布局中
        message_box.Add(self.seemsg_top,5,wx.EXPAND | wx.CENTER | wx.ALL,border = 5)
        message_box.Add(sendmessage_box,1,wx.EXPAND | wx.CENTER | wx.ALL,border = 5)

        self.fatherpanel.SetSizer(message_box)

    def OnBtnOk(self,event):
        if self.sendmsg_bottom.GetValue() != '':
            #datetime 模块中的today函数获取当天的时间
            now_time = datetime.datetime.today()
            #格式化输出时间
            str_now_time = now_time.strftime('%Y-%m-%d %H:%M:%S')

            #将发送的消息显示在聊天框中
            msg = '您对{1}说：   #{0}#：\n{2}\n'.format(str_now_time,self.friend['user_name'],self.sendmsg_bottom.GetValue())

            #将发送的消息保存到一个成员变量中，日志信息
            self.msglog += msg
            #在查看框中显示日志
            self.seemsg_top.SetValue(self.msglog)
            #将光标设置在最后一行
            self.seemsg_top.SetInsertionPointEnd()

            #将要发送的数据发送给服务器
            json_obj = {}
            json_obj['command'] = COMMAND_SENDMSG
            json_obj['user_id'] = self.user['user_id']
            json_obj['message'] = self.sendmsg_bottom.GetValue()
            json_obj['receive_user_id'] = self.friend['user_id']

            #将数据编码
            json_str = json.dumps(json_obj)
            #发送数据
            client_socket.sendto(json_str.encode(),sever_address)
            #清空消息发送文本框
            self.sendmsg_bottom.SetValue('')

    def thread_body(self):
        while self.running:
            try:
                json_data,_ = client_socket.recvfrom(1024)
                json_obj = json.loads(json_data.decode())
                logger.info('从服务器接收数据{0}'.format(json_obj))
                command = json_obj['command']

                if command is not None and command == COMMAND_REFRESH:
                    userid = json_obj['OnlineUserList']
                    self.FriendFrame.RefreshFriendList(userid)
                else:
                    # 获取时间
                    now_time = datetime.datetime.today()
                    # 格式化时间输出
                    str_now_time = now_time.strftime('%Y-%m-%d  %H:%M:%S')

                    # 将对方发过来的消息显示在聊天窗口中
                    message = json_obj['message']

                    msg = '{1}对您说：{0}\n  {2} \n'.format(str_now_time, self.friend['user_name'], message)
                    self.msglog += msg
                    # 在聊天窗口中显示好友发送过来的消息
                    self.seemsg_top.SetValue(self.msglog)
                    # 光表现是在最后一行
                    self.seemsg_top.SetInsertionPointEnd()

            except Exception:

                continue