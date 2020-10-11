import modules.service as service
import os

os.environ['DEBUG'] = 'True'

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

    Beautiful Ghosts
    Christmas Tree Farm
    Eyes Open
    Lover Shawn Mendes Remix
    Only The Young

'''.lower(), 'yntcd')