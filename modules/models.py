from .sqlinit import SQLInit
import sqlite3

sql = SQLInit()

class Acronym(object):
    id = 1
    acronym = ''
    artist = ''
    album = ''
    album_year = ''
    song = ''
    subreddit_ids = ''
    is_artist = False
    is_album = False
    is_song = False
    is_single = False

    def __init__(self, id, acronym, artist, album, album_year, song, subreddit_ids, is_artist, is_album, is_song, is_single):
        self.id = id
        self.acronym = acronym
        self.artist = artist
        self.album = album
        self.album_year = album_year
        self.song = song
        self.subreddit_ids = subreddit_ids
        self.is_artist = is_artist
        self.is_album = is_album
        self.is_song = is_song
        self.is_single = is_single

class Redditor(object):
    id = 1
    name = ""
    enabled = False

    def __init__(self, id, name, enabled):
        self.id = id
        self.name = name
        self.enabled = enabled

class Subreddit(object):
    id = 0
    name = ""
    enabled = 0

    def __init__(self, id, name, enabled):
        self.id = id
        self.name = name
        self.enabled = enabled