from .sqlinit import SQLInit
import sqlite3

sql = SQLInit()

class Blacklist(object):
    id = 1
    redditor = ""
    blacklisted = 0

    def __init__(self, id, redditor, blacklisted):
        self.id = id
        self.redditor = redditor
        self.blacklisted = blacklisted

class Comment(object):
    id = 1
    submission_id = 1
    comment_id = 1
    replied = 0

    def __init__(self, id, submission_id, comment_id, replied):
        self.id = id
        self.submission_id = submission_id
        self.comment_id = comment_id
        self.replied = replied

class Keyword(object):
    id = 1
    keyword = ""
    comment_text = ""

    def __init__(self, id, keyword, comment_text):
        self.id = id
        self.keyword = keyword
        self.comment_text = comment_text