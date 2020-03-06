import pymysql
import configparser
import logging

logger = logging.getLogger(__name__)

class BaseDao(object):
    def __init__(self):
        #创建一个读取config文件的parser解析器
        self.config = configparser.ConfigParser()
        self.config.read('config.ini',encoding='utf-8')

        host = self.config['db']['host']
        user = self.config['db']['user']
        port = self.config.getint('db','port')
        password = self.config['db']['password']
        database = self.config['db']['database']
        charset = self.config['db']['charset']

        self.conn = pymysql.connect(host = host,
                                    user = user,
                                    port = port,
                                    password = password,
                                    database = database,
                                    charset = charset)

    def Cloose(self):
        self.conn.close()