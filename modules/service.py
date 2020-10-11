from .models import Blacklist, Comment, Keyword
from .repository import add_comment, author_is_disabled, get_all_keywords_by_subreddit, is_reply_limit_reached, get_all_subreddits
import praw
import time

def get_enabled_subreddits():
    subreddits = ""
    for subreddit in get_all_subreddits():
        if subreddit.enabled:
            if subreddits == "":
                subreddits += subreddit.name
            else:
                subreddits += f"+{subreddit.name}"

    print(f"Monitoring the following subreddits: {subreddits}")
    
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

    # If this post has a title property then it is a submission.
    if hasattr(post, 'title'):
        print(f"SUBMISSION {post.permalink} :: {post.title}")
        process_submission(post)

    # Otherwise, this post is a comment.
    else:
        print(f"COMMENT {post.permalink} :: {post.body}")
        process_comment(post)

def process_comment(comment : praw.models.Comment):
    reply_text = format_reply(comment)

    if reply_text != "":
        try:
            comment.reply(reply_text)
            add_comment(comment.submission.id, comment.id, 1)
        except:
            print("Processing of comment failed!")
    else:
        print('SKIPPING :: No matching keyword.')

def process_submission(submission : praw.models.Submission):
    reply_text = format_reply(submission)

    if reply_text != "":
        try:
            submission.reply(reply_text)
            add_comment(submission.id, None, 1)
        except:
            print("Processing of submission failed!")
    else:
        print('SKIPPING :: No matching keyword.')

def should_delete(post):
    if hasattr(post, 'title'):
        return False

    match = is_match(post.body.lower(), 'delete')

    if not post.is_root and match != -1:
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
    submission_id = post.id

    if hasattr(post, 'body'):
        submission_id = post.submission.id

    if post.author.name == "songacronymbot":
        return False

    if time.time() - post.created_utc > 180:
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
    
    if is_reply_limit_reached(submission_id, 5):
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

def format_reply(post):
    reply_text = get_comment_text(post)

    if reply_text != "":
        return add_footer(post.author.name, reply_text)

    return reply_text

def get_comment_text(post):
    keywords = get_all_keywords_by_subreddit(post.subreddit.id)

    text = ""
    if hasattr(post, 'title'):
        text = f"{post.title.lower()} {post.selftext.lower()}"
    else:
        text = post.body.lower()

    comment_text = ""
    
    for keyword in keywords:
        if is_match(text, keyword.keyword.lower()):
            comment_text += f"- {keyword.comment_text}\n"
            
    return comment_text


def is_match(text, keyword):
    match = text.find(keyword)
    if match != -1:
        if match > 0:
            start = match - 1
        else:
            start = match

        end = match + len(keyword) + 1

        word = text[start:end]
        word = "".join(char for char in word if char.isalnum())
        if word == keyword:
            return True

    return False
    

def add_footer(author, text: str):
    return f"{text}\n---\n\n^(This is an automated reply. | /u/{author} can reply with \"delete\" to remove this comment. | DM for inquiries/feedback/opt-out.)"