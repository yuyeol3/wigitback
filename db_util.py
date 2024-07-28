import sqlite3


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
        CREATE TABLE IF NOT EXISTS documents (
            doc_name PRIMARY KEY            
        );
        ''')
        con.commit()
    except Exception as err:
        print(err)
    finally:
        db_close(con, cur)


init_db()