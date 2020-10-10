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

def add_comment(submission_id: str, comment_id: str, replied: int):
    sql.cur.execute("INSERT INTO Comments (SubmissionId, CommentId, Replied) VALUES (?, ?, ?)", [submission_id, comment_id, replied])
    sql.conn.commit()

def is_reply_limit_reached(submission_id : str, reply_limit : int):
    sql.cur.execute("SELECT COUNT(*) FROM Comments WHERE SubmissionId = ? AND Replied = 1", [submission_id])
    result = sql.cur.fetchone()
    if result[0] >= reply_limit:
        return True

    return False

def get_all_keywords():
    keywords = []
    for row in sql.cur.execute("SELECT Id, Keyword, CommentText FROM Keywords"):
        keywords.append(Keyword(row[0], row[1], row[2]))
        
    return keywords