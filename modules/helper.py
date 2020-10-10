from .models import Blacklist, Comment, Keyword
from .repository import add_comment, author_is_blacklisted, get_all_keywords, is_reply_limit_reached
import praw
import time

# Initialize list of keywords we are looking for.
keywords = get_all_keywords()

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
    reply_text = format_reply(comment.author.name, comment.body.lower())

    if reply_text != "":
        try:
            comment.reply(reply_text)
            add_comment(comment.submission.id, comment.id, 1)
        except:
            print("Processing of comment failed!")

def process_submission(submission : praw.models.Submission):
    reply_text = format_reply(submission.author.name, f"{submission.title.lower()} {submission.selftext.lower()}")

    if reply_text != "":
        try:
            submission.reply(reply_text)
            add_comment(submission.id, None, 1)
        except:
            print("Processing of submission failed!")

def should_delete(post):
    if hasattr(post, 'title'):
        return False

    match = find_match(post.body.lower(), 'delete')

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
        print('SKIPPING :: Bot is author.')
        return False

    if time.time() - post.created_utc > 300:
        print('SKIPPING :: Post older than 5 minutes.')
        return False

    if is_summon_chain(post):
        print('SKIPPING :: Summon chain.')
        return False

    if is_already_replied(post):
        print('SKIPPING :: Already replied to.')
        return False

    if author_is_blacklisted(post.author.name):
        print('SKIPPING :: Author is blacklisted.')
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

def format_reply(author, text : str):
    reply_text = get_comment_text(text)

    if reply_text != "":
        return add_footer(author, reply_text)

    return reply_text

def get_comment_text(text : str):
    comment_text = ""
    for keyword in keywords:
        match = find_match(text, f" {keyword.keyword.lower()} ")
        
        if match == -1:
            match = find_match(text, f"{keyword.keyword.lower()}\"")
        if match == -1:
            match = find_match(text, f"{keyword.keyword.lower()})")
        if match == -1:
            match = find_match(text, f" {keyword.keyword.lower()}:")
        if match == -1:
            match = find_match(text, f" {keyword.keyword.lower()};")
        if match == -1:
            match = find_match(text, f" {keyword.keyword.lower()}]")
        if match == -1:
            match = find_match(text, f" {keyword.keyword.lower()}:")
        if match == -1:
            match = find_match(text, f"{keyword.keyword.lower()}'")

        if match != -1:
            comment_text += f"- {keyword.comment_text}\n"
            
    return comment_text

def find_match(text, keyword):
    return text.find(keyword)

def add_footer(author, text: str):
    return f"{text}\n---\n\n^(_I am a bot. | /u/{author} may reply with `delete` to remove comment. | DM for inquiries/feedback/opt-out._)"

