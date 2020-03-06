from com.zhouhui.qq.server.base_dao import BaseDao


class UserDao(BaseDao):
    def __init__(self):
        super().__init__()

    def findbyid(self,userid):
        try:
            with self.conn.cursor() as cursor:
                sql = 'select user_id,user_password,user_name,user_icon from users where user_id = %s'
                cursor.execute(sql,userid)

                row = cursor.fetchone()

                if row is not None:
                    user = {}
                    user['user_id'] = row[0]
                    user['user_password'] = row[1]
                    user['user_name'] = row[2]
                    user['user_icon'] = row[3]
                    return user

        finally:
            self.conn.close()


    def findbyfriends(self,userid):
        users = []
        try:
            with self.conn.cursor() as cursor:
                sql = 'select user_id,user_password,user_name,user_icon from users where user_id in (select user_id2 as user_id from friends where user_id1 = %s) or user_id in (select user_id1 as user_id from friends where user_id2 = %s)'

                cursor.execute(sql,(userid,userid))

                result_set = cursor.fetchall()

                for row in result_set:
                    user = {}
                    user['user_id'] = row[0]
                    user['user_password'] = row[1]
                    user['user_name'] = row[2]
                    user['user_icon'] = row[3]

                    users.append(user)

        finally:
            self.conn.close()

        return users