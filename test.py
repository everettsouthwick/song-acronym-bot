import modules.service as service
import praw
import os

os.environ['DEBUG'] = 'True'

r = praw.Reddit("songacronymbot")

def test_comment_opt_out():
    post = r.comment(id="g8mfil8")
    print(post.submission.id)

    if service.should_opt_out(post):
        print('This is an opt-out post!')

test_comment_opt_out()

def test_match(comment, keyword):
    if service.is_match(comment, keyword):
        print(f"{keyword} was found!")
    else:
        print("No matches found!")

test_match('''Here is my current list of all lyric videos. I am certain there are more, and will add on if I find any, or if yall mention any.

Red

    WANEGBT

Reputation

    Gorgeous
    LWYMMD
    CIWYW

Lover

    Lover
    ME!
    The Archer
    YNTCD
    The Man

Other

    ma&thp
    Christmas Tree Farm
    Eyes Open
    Lover Shawn Mendes Remix
    Only The Young

'''.lower(), 'ma&thp')