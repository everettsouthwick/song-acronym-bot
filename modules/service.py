from .models import Acronym, Redditor, Subreddit
from .repository import add_or_update_redditor, author_is_disabled, get_all_acronyms_by_subreddit, get_all_subreddits
import praw
import time
import os

debug = bool(os.getenv('DEBUG') == 'True')

def get_enabled_subreddits():
    subreddits = ""
    for subreddit in get_all_subreddits():
        if subreddit.enabled:
            if subreddits == "":
                subreddits += subreddit.name
            else:
                subreddits += f"+{subreddit.name}"

    if debug:
        print(f"SUBREDDITS :: Monitoring the following subreddits: {subreddits}")
    
    return subreddits

def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def process_post(post):
    if should_delete(post):
        return

    if not should_comment(post):
        return

    if should_opt_out(post):
        return

    # If this post has a title property then it is a submission.
    if hasattr(post, 'title'):
        if debug:
            print(f"SUBMISSION {post.permalink} :: {post.title}")
        process_submission(post)

    # Otherwise, this post is a comment.
    else:
        if debug:
            print(f"COMMENT {post.permalink} :: {post.body}")
        process_comment(post)

def process_comment(comment : praw.models.Comment):
    reply_text = format_reply(comment)

    if reply_text != "":
        try:
            comment.reply(reply_text)
        except:
            print("ERROR :: Processing of comment failed!")
    else:
        if debug:
            print('SKIPPING :: No matching keyword.')

def process_submission(submission : praw.models.Submission):
    reply_text = format_reply(submission)

    if reply_text != "":
        try:
            submission.reply(reply_text)
        except:
            print("ERROR :: Processing of submission failed!")
    else:
        if debug:
            print('SKIPPING :: No matching keyword.')

def should_opt_out(post):
    if hasattr(post, 'title'):
        return False

    submission = post.submission
    if submission.id == 'j9yq8q':
        if (is_match(post.body.lower(), 'optout')):
            add_or_update_redditor(post.author.id, post.author.name, '0')
            post.reply(add_footer(post, f"- Your account has been disabled from receiving automatic replies.\n"))
            return True

        # elif (is_match(post.body.lower(), 'optin')):
        #     add_or_update_redditor(post.author.id, post.author.name, '1')
        #     post.reply(add_footer(post, f"- Your account has been enabled to receive automatic replies. To disable your account from receiving automatic replies, reply to this thread with `optout`.\n"))
        #     return True

    return False

def should_delete(post):
    if hasattr(post, 'title'):
        return False

    if not post.is_root:
        if is_match(post.body.lower(), 'delete'):
            parent = post.parent()
            # Check if the parent comment is from us.
            if parent.author != None and parent.author.name == 'songacronymbot':
                comment_to_delete = parent
                parent = parent.parent()
                # Check to see if the parent of our comment is from the same author requesting the deletion.
                if parent.author != None and parent.author.name == post.author.name:
                    # If it is, delete the comment.
                    comment_to_delete.delete()
                    return True
                else:
                    print('SKIPPING :: Redditor requesting deletion is not the original author.')
    
    return False

def should_comment(post):
    if post.author.name == "songacronymbot":
        return False

    if time.time() - post.created_utc > 1800:
        return False

    if is_summon_chain(post):
        print('SKIPPING :: Summon chain.')
        return False

    if is_already_replied(post):
        print('SKIPPING :: Already replied to.')
        return False

    if author_is_disabled(post.author.name):
        print('SKIPPING :: Author is disabled.')
        return False
    
    if is_reply_limit_reached(post, 5):
        print('SKIPPING :: Reply limit reached.')
        return False

    return True

def is_summon_chain(post):
    if hasattr(post, 'title'):
        return False

    if not post.is_root:
        parent = post.parent()
        if parent.author != None and parent.author.name == 'songacronymbot':
            return True
    
    return False

def is_already_replied(post):
    replied = False
    replies = None

    if hasattr(post, 'title'):
        replies = post.comments
    else:
        post.refresh()
        replies = post.replies

    reply_count = len(list(replies))

    if reply_count != 0:
        for reply in replies:
            if reply.author != None and reply.author.name == 'songacronymbot':
                replied = True
                break

    return replied

def is_reply_limit_reached(post, limit):
    count = 0

    if hasattr(post, 'title'):
        submission = post
    else:
        submission = post.submission
    
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        try:
            if comment.author.name == 'songacronymbot':
                count = count + 1
        except:
            pass
    
    if count >= limit:
        return True

    return False

def format_reply(post):
    reply_text = get_comment_text(post)

    if reply_text != "":
        return add_footer(post, reply_text)

    return reply_text

def get_comment_text(post):
    acronyms = get_all_acronyms_by_subreddit(post.subreddit.id)

    text = ""
    if hasattr(post, 'title'):
        text = f"{post.title.lower()} {post.selftext.lower()}"
    else:
        text = post.body.lower()

    comment_text = ""
    
    for acronym in acronyms:
        if is_match(text, acronym.acronym.lower()):
            if unique_acronym(post, acronym.acronym.lower()):
                if  acronym.is_artist and undefined_acronym(post, acronym.artist.lower()):
                    comment_text += f"- {acronym.acronym} refers to {acronym.artist}.\n"

                elif acronym.is_album and undefined_acronym(post, acronym.album.lower()):
                    comment_text += f"- {acronym.acronym} refers to *{acronym.album}* ({acronym.album_year}), an album by {acronym.artist}.\n"

                elif acronym.is_single and undefined_acronym(post, acronym.song.lower()):
                    comment_text += f"- {acronym.acronym} refers to \"{acronym.song}\", a single from {acronym.artist}.\n"

                elif acronym.is_song and undefined_acronym(post, acronym.song.lower()):
                    comment_text += f"- {acronym.acronym} refers to \"{acronym.song}\", a song from {acronym.artist} album *{acronym.album}* ({acronym.album_year}).\n"

            
    return comment_text

def unique_acronym(post, acronym):
    if hasattr(post, 'title'):
        submission = post
    else:
        submission = post.submission
    
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        if comment.author.name == 'songacronymbot':
            if acronym in comment.body.lower():
                return False
    
    return True

def undefined_acronym(post, definition):
    if hasattr(post, 'title'):
        submission = post
    else:
        submission = post.submission

    if hasattr(post, 'body'):
        if definition in post.body.lower():
                return False
        
        if not post.is_root:
            parent = post.parent()
            if definition in parent.body.lower():
                return False

    if definition in submission.title.lower() or definition in submission.selftext.lower():
        return False

    return True


def is_match(text, keyword):
    if debug:
        print(f"is_match(text: {text}, keyword: {keyword})")

    match = text.find(keyword)
    if match != -1:
        if match > 0:
            start = match - 1
        else:
            start = match

        end = match + len(keyword) + 1

        # We want to remove all the special characters from our word.
        word = text[start:end]
        word = "".join(char for char in word if char.isalnum() or char == '&' or char == '-')

        if debug:
            print(f"is_match() word: {word}")

        if word == keyword:
            return True

    return False
    
def add_footer(post, text: str):
    return f"{text}\n---\n\n^[/u/{post.author.name}](/u/{post.author.name}) ^(can reply with \"delete\" to remove comment. |) ^[/r/songacronymbot](/r/songacronymbot) ^(for feedback.)"