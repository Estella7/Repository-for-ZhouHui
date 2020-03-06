import logging
import socket
import sys
import json
import traceback as tb

from com.zhouhui.qq.server.user_dao import UserDao

logger = logging.getLogger(__name__)
#logging 模块默认只输出warning级别以上的内容，以下的都不会输出，所以这里修改级别是为了让info输出
logging.basicConfig(level=logging.NOTSET)


#服务器IP
SERVER_IP = '127.0.0.1'
#服务器端口号
SERVER_PORT = 8888
#服务器地址
server_address = (SERVER_IP,SERVER_PORT)

#操作命令代码
COMMAND_LOGIN = 1
COMMAND_LOGOUT = 2
COMMAND_SENDMSG = 3
COMMAND_REFRESH = 4


#保存用户信息的一个列表
clientlist = []

#创建socket对象，并绑定IP和端口号
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP,SERVER_PORT))

logger.info('服务器启动，监听自己的端口{0}...'.format(SERVER_PORT))

buffer = []

while True:
    try:
        #获取数据，提取data和地址
        data,client_address = server_socket.recvfrom(1024)
        #对从客户端获取到的json数据解码
        json_obj = json.loads(data.decode())
        logger.info('接收客户端消息:{0}...'.format(json_obj))

        #获取客户端传过来的操作命令
        command = json_obj['command']

        if command == COMMAND_LOGIN:
            userid = json_obj['user_id']
            userpassword = json_obj['user_password']
            print(1)
            #输出日志
            logger.debug('user_id:{0}  user_password:{1}'.format(userid,userpassword))

            #导入用户dao
            dao = UserDao()
            #通过用户ID查询
            user = dao.findbyid(userid)
            #输出用户信息

            logger.info(user)
            if user is not None and user['user_password'] == userpassword:
                logger.info('登录成功')
                #保存用户信息
                clientinfo = (userid,client_address)

                #将用户信息保存起来
                clientlist.append(clientinfo)

                #给客户端准备数据
                json_obj = user
                json_obj['result'] = '0'#0是在线，-1是不在线

                #取出用户的好友列表
                dao = UserDao()
                friends = dao.findbyfriends(userid)

                #使用map函数从在线用户当中取出元素的ID
                cinfo_userid = map(lambda t:t[0],clientlist)

                for friend in friends:
                    fid = friend['user_id']
                    #添加好友状态，1在线，0离线
                    friend['online'] = '0'

                    #如果fid用户ID在clientlist中，说明这个用户在线，也就是这个好友在线
                    if fid in cinfo_userid:
                        friend['online'] = '1'

                #将增加了online的friends替换掉json对象中原有的数据
                json_obj['friends'] = friends
                logger.info('服务器发送用户登录成功，消息{}'.format(json_obj))

                #将惊悚json对象进行编码
                json_str = json.dumps(json_obj)
                #给客户端发送数据
                server_socket.sendto(json_str.encode(),client_address)

            else:

                json_obj = {}
                json_obj['result'] = '-1'
                #json编码
                json_str = json.dumps(json_obj)
                #给客户端发送数据
                server_socket.sendto(json_str.encode(),client_address)

        elif command == COMMAND_SENDMSG:
            #获取好友id
            friend_id = json_obj['receive_user_id']
            #在clientlist中查找好友的ID，lambda函数：让t的第一个数据等于好友对的ID，如果找到就通过filter函数过滤出来
            filter_clientinfo = filter(lambda t:t[0] == friend_id,clientlist)
            clientinfo = list(filter_clientinfo)
            #如果filter函数能找到好友的ID，说明好友在线，那么clientinfo就应该有一条数据，表明这个好友在线
            if len(clientinfo) == 1:
                #从clientinfo中提取出该用户的端口和主机地址
                _,client_address = clientinfo[0]
                #向客户端发送数据
                json_str = json.dumps(json_obj)
                server_socket.sendto(json_str.encode(),client_address)

        elif command == COMMAND_LOGOUT:
            #获取用户ID
            user_id = json_obj['user_id']
            for clientinfo in clientlist:
                out_userid,_ = clientinfo
                if out_userid == user_id:
                    clientlist.remove(clientinfo)
                    break
            logger.info(clientlist)


        #刷新好友列表
        if len(clientlist) == 0:
            continue

        json_obj = {}
        #提取从客户端接收数据中的command的数据
        json_obj['command'] = COMMAND_REFRESH
        #map函数，提取用户的ID，确切的说应该是索引
        userid_map = map(lambda t:t[0],clientlist)
        userid_list = list(userid_map)
        json_obj['OnlineUserList'] = userid_list

        for clientinfo in clientlist:
            #第一个数据是客户端ID，第二个是客户端地址，此处只需要地址用来发送数据，ID不需要
            _,address = clientinfo
            #给数据编码，并发送到客户端
            json_str = json.dumps(json_obj)
            server_socket.sendto(json_str.encode(),address)

    except Exception:
        tb.print_exc()
        logger.info('超时')