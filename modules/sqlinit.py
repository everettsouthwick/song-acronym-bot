from .config import config
import psycopg2

class SQLInit:
    def __init__(self):
        dbParams = config("creds")
        self.conn = psycopg2.connect(**dbParams)
        self.cur = self.conn.cursor()