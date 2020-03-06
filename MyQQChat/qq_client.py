import wx
import logging

from com.zhouhui.qq.client.login_frame import LoginFrame


#设置日志输出格式
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')

logger =logging.getLogger(__name__)

class App(wx.App):
    def OnInit(self):
        frame = LoginFrame()
        frame.Show()

        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()