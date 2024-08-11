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

        cur.execute('''
        CREATE TABLE IF NOT EXISTS redirections (
            redirect_id TEXT PRIMARY KEY,
            original_doc TEXT NOT NULL            
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

        cur.execute('''INSERT INTO users VALUES(?, ?, ?, ?, ?);''',
                    (user_id, hashed_pwd.decode("utf-8"), email, today_str, user_type))
        con.commit()
    
    except Exception as err:
        print(err)
    finally:
        db_close(con, cur)


def add_redirections(doc_name, redirections):
    con, cur = get_db_con("database.db")
    redirection_set = set(redirections.split(","))

    # 1. 기존 목록과 새 리디렉션을 비교.
    # 2. 없어진 건 삭제
    # 3. 새로 생긴 건 추가.
    # 4. 기존에 다른 문서걸로 있으면 걍 생까기(선점)
    try:
        cur.execute('''
            SELECT redirect_id FROM redirections
            WHERE original_doc=?;
        ''', (doc_name,))

        res = cur.fetchall()
        ids = set([i[0] for i in res])

        to_remove = ids - redirection_set
        to_add = redirection_set - ids

        for e in to_remove:
            cur.execute('''
                DELETE FROM redirections
                WHERE redirect_id=? AND original_doc=?;
            ''', (e, doc_name))

            con.commit()

        for e in to_add:
            cur.execute("SELECT COUNT(*) FROM redirections WHERE redirection_id=?;", (e))
            res = int(cur.fetchone()[0])

            if (res == 0):
                cur.execute('''
                    INSERT INTO redirections
                    VALUES(?, ?);
                ''', (e, doc_name))




    except Exception as err:
        print(err)
    finally:
        db_close(con,cur)

init_db()