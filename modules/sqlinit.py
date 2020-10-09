import sqlite3

class SQLInit:
    def __init__(self):
        self.conn = sqlite3.connect("main.db")
        self.cur = self.conn.cursor()
        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS "Comments" (
                        "Id"	INTEGER NOT NULL UNIQUE,
                        "CommentId"	INTEGER NOT NULL UNIQUE,
                        "Replied"	INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY("Id" AUTOINCREMENT)
                    )
                ''')
        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS "Keywords" (
                        "Id"	INTEGER NOT NULL UNIQUE,
                        "Keyword"	TEXT NOT NULL UNIQUE,
                        "CommentText"	TEXT NOT NULL UNIQUE,
                        PRIMARY KEY("Id" AUTOINCREMENT)
                    )
                ''')
        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS "Blacklist" (
                        "Id"	INTEGER NOT NULL UNIQUE,
                        "Redditor"	TEXT NOT NULL UNIQUE,
                        "Blacklisted"	INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY("Id" AUTOINCREMENT)
                    )
                ''')
        self.conn.commit()