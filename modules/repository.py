from .models import Keyword
from .sqlinit import SQLInit
import sqlite3

sql = SQLInit()

def author_is_blacklisted(redditor : str):
    sql.cur.execute("SELECT * FROM Blacklist WHERE Redditor = ? AND Blacklisted = 1", [redditor])
    result = sql.cur.fetchone()
    if result:
        return True

    return False

def add_comment(comment_id: int, replied: int):
    sql.cur.execute("INSERT INTO Comments (CommentId, Replied) VALUES (?, ?)", [comment_id, replied])
    sql.conn.commit()

def comment_is_replied(comment_id : int):
    sql.cur.execute("SELECT * FROM Comments WHERE CommentId = ? AND Replied = 1", [comment_id])
    result = sql.cur.fetchone()
    if result:
        return True
    
    return False

def get_all_keywords():
    keywords = []
    for row in sql.cur.execute("SELECT Id, Keyword, CommentText FROM Keywords"):
        keywords.append(Keyword(row[0], row[1], row[2]))
        
    return keywords