from flask_login import UserMixin
import utils.db as db
from utils.db import USER_PERMS as PERM
import traceback
from datetime import datetime
import bcrypt
from utils.perms import MANAGER_PERM

class User(UserMixin):
    MANAGER_PERM = MANAGER_PERM

    def __init__(self, user_id, registered_date, user_type, email):
        self.user_id = user_id
        self.registered_date = registered_date
        self.user_type = user_type
        self.email = email

    def get_id(self):
        return self.user_id
    
    
    def get_user_status(self):
        '''사용자 suspended 상태'''
        if (self.user_type == "SUS"):
            return "정지"
        else:
            return "일반"
        
    def get_user_permission(self, perm_target):
        return User.MANAGER_PERM[perm_target][self.user_type]
    
    @staticmethod
    def get_user_info(user_id, user_pw=None):
        result = {"result" : "succeed", "count" : 0 }

        try:
            params = [user_id]
            sql = ""
            sql += "SELECT id, email, registered_date, type_id FROM users"
            if user_pw is None:
                sql += " WHERE id=?"
            else:
                sql += " WHERE id=? AND password=?"
                params.append(user_pw)

            sql += ";"

            con, cur = db.get_db_con("database.db")
            cur.execute(sql, params)
            fetchres = cur.fetchone()

            if (fetchres is not None):
                result = {
                    'result' : 'succeed',
                    'count'  : 1,
                    'data' : {
                        'id' : fetchres[0],
                        'email' : fetchres[1],
                        'registered_date' : datetime(*map(int, fetchres[2].split("/"))),
                        'type_id' : fetchres[3]
                    }
                }


        except Exception as err:
            traceback.print_exc()
            result['result'] = 'fail'
            result['data']   = err

        finally:
            db.db_close(con, cur)
            return result


