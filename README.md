# song-acronym-bot
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightscreen.svg)

Simple bot for Reddit that replies to comments and submissions containing song acronyms with the full song title.

## Dependencies

- [Python3.6+](https://www.python.org/downloads/)
- [Praw](https://praw.readthedocs.io/en/latest/getting_started/installation.html)

## Getting Started

1. Clone or download the project
2. Copy [`praw.ini.sample`](praw.ini.sample) to `praw.ini` and modify it with your details
3. Execute `python song_acronym_bot.py`

## Features

* Replies to comments and submissions that contain song acronyms with full song title
* Anti-spam & anti-abuse measures
* Opt-out on user basis, original author can delete comment by replying with `delete`

## TODO

- Add tests
- Add more subreddits on opt-in basis
