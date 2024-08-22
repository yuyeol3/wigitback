import sqlite3
from datetime import datetime
import traceback
import bcrypt
from utils.funcs import get_doc_list

SALT = b'$2b$12$vVbvdvSW3xlSGYh9y4ygp.'

def get_db_con(filename):
    con = sqlite3.connect(filename)
    cur = con.cursor()

    return con, cur

def db_close(con, cur):
    cur.close()
    con.close()

def init_db(ignitive_run=False):
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

        # 사용자 타입 레코드 추가
        if (ignitive_run):
            cur.execute("INSERT INTO user_type VALUES('ADM', '관리자')")
            cur.execute("INSERT INTO user_type VALUES('OPR', '운영자')")
            cur.execute("INSERT INTO user_type VALUES('USR', '사용자')")
            cur.execute("INSERT INTO user_type VALUES('SUS', '정지')")

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

def set_user(user_id, pwd=None, email=None, user_type=None):
    con, cur = get_db_con("database.db")

    try:
        if (pwd is not None):
            hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), SALT)
            cur.execute("UPDATE users SET pwd=? WHERE user_id=?", (hashed_pwd, user_id))

        if (email is not None):
            cur.execute("UPDATE users SET email=? WHERE user_id=?", (email, user_id))

        if (user_type is not None):
            cur.execute("UPDATE users SET type_id=? WHERE user_id=?", (user_type, user_id))
        
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
        to_remove.add(doc_name)
        # print(to_remove)
        # print(to_add)

        for e in to_remove:
            cur.execute('''
                DELETE FROM redirections
                WHERE redirect_id=? AND original_doc=?;
            ''', (e, doc_name))

            con.commit()

        added = set()
        for e in to_add:
            # cur.execute("SELECT COUNT(*) FROM redirections WHERE redirect_id=?;", (e,))
            # res = int(cur.fetchone()[0])
            id_occupied = check_redirections(e)[0]

            if (id_occupied is False and 
                e not in get_doc_list("./documents") and 
                e !="" and 
                e != doc_name):
                cur.execute('''
                    INSERT INTO redirections
                    VALUES(?, ?);
                ''', (e, doc_name))
                added.add(e)

        con.commit()

        # print((ids - to_remove).union(added))
        return (ids - to_remove).union(added)
    except Exception as err:
        print(err)
    finally:
        db_close(con,cur)

def check_redirections(check_id : str) -> tuple[bool, str]:
    con, cur = get_db_con("database.db")

    try:
        cur.execute("SELECT COUNT(*), original_doc FROM redirections WHERE redirect_id=?;",
                    (check_id,))
        res = cur.fetchone()
        # print(res)
        return (res[0] >= 1, res[1])

    except Exception as err:
        traceback.print_exc()
        return (False, "")
    finally:
        db_close(con,cur)

def update_redirections(prev_id, changed_id):
    '''
        기존에 original_doc 이 prev_id로 지정되어 있던 레코드를
        changed_id로 변경하고, prev_id -> changed_id로 이동시키는 리디렉션을 생성
    '''
    con, cur = get_db_con("database.db")

    try:
        cur.execute('''
            UPDATE redirections
            SET original_doc=?
            WHERE original_doc=?;

        ''', (changed_id, prev_id))

        cur.execute('''
            INSERT INTO redirections
            VALUES(?, ?)
        ''', (prev_id, changed_id))
        con.commit()
        return True

    except Exception as err:
        traceback.print_exc()
        return False
    
    finally:
        db_close(con,cur)

init_db()