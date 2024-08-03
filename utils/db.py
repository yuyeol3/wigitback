import sqlite3
from datetime import datetime
import traceback
import bcrypt

SALT = b'$2b$12$vVbvdvSW3xlSGYh9y4ygp.'

def get_db_con(filename):
    con = sqlite3.connect(filename)
    cur = con.cursor()

    return con, cur

def db_close(con, cur):
    cur.close()
    con.close()

def init_db():
    con, cur = get_db_con("database.db")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS user_type (
            type_id TEXT PRIMARY KEY,
            type_name TEXT NOT NULL        
        );
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            registered_date TEXT NOT NULL,
            type_id TEXT DEFAULT 'USR',
            FOREIGN KEY (type_id) REFERENCES user_type(type_id)                      
        );
        ''')
        con.commit()
    except Exception as err:
        traceback.print_exc()
    finally:
        db_close(con, cur)

def add_user(user_id, pwd, email, user_type="USR"):
    hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), SALT)
    con, cur = get_db_con("database.db")


    try:
        today = datetime.today()
        today_str = f"{today.year}/{today.month}/{today.day}"

        cur.execute('''INSERT INTO users VALUES(?, ?, ?, ?, ?)''',
                    (user_id, hashed_pwd.decode("utf-8"), email, today_str, user_type))
        con.commit()
    
    except Exception as err:
        print(err)
    finally:
        db_close(con, cur)




init_db()