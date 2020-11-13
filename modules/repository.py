from .models import Acronym, Subreddit
from .sqlinit import SQLInit
import psycopg2

def get_all_subreddits():
    subreddits = []

    sql = SQLInit()
    
    sql.cur.execute('SELECT id, name, enabled FROM "public"."subreddit"')
    for row in sql.cur:
        subreddits.append(Subreddit(row[0], row[1], row[2]))

    sql.conn.close()
    
    return subreddits

def author_is_disabled(name : str):
    sql = SQLInit()

    sql.cur.execute('SELECT * FROM "public"."redditor" WHERE name = %s AND enabled = \'0\'', [name])
    result = sql.cur.fetchone()

    sql.conn.close()

    if result:
        return True

    return False

def add_or_update_redditor(id : str, name : str, enabled : int):
    sql = SQLInit()

    try:
        # Try to insert the record.
        sql.cur.execute('INSERT INTO "public"."redditor" (id, name, enabled) VALUES (%s, %s, %s)', [id, name, enabled])
        sql.conn.commit()
        sql.conn.close()
    except:
        # If this fails, then it must be an update.
        sql.cur.execute('UPDATE "public"."redditor" SET enabled = %s WHERE id = %s', [enabled, id])
        sql.conn.commit()
        sql.conn.close()

def get_all_acronyms_by_subreddit(id : str):
    acronyms = []

    sql = SQLInit()
    sql.cur.execute('SELECT id, acronym, artist, album, album_year, song, subreddit_ids, is_artist, is_album, is_song, is_single FROM "public"."acronym" WHERE subreddit_ids LIKE %s OR subreddit_ids = \'global\'', [f'%{id}%'])
    for row in sql.cur:
        acronyms.append(Acronym(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

    sql.conn.close()

    return acronyms