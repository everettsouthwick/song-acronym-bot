from .models import Blacklist, Comment, Keyword
from .repository import add_comment, author_is_blacklisted, comment_is_replied, get_all_keywords
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
    reply_text = format_reply(comment.body.lower())

    if reply_text != "":
        try:
            comment.reply(reply_text)
            add_comment(comment.id, 1)
        except:
            print("Processing of comment failed!")

def process_submission(submission : praw.models.Submission):
    reply_text = format_reply(f"{submission.title.lower()} {submission.selftext.lower()}")

    if reply_text != "":
        try:
            submission.reply(reply_text)
            add_comment(submission.id, 1)
        except:
            print("Processing of submission failed!")



def should_comment(post):
    if post.author.name == "songacronymbot":
        return False

    if time.time() - post.created_utc > 300:
        return False

    if author_is_blacklisted(post.author.name):
        print(f"{post.author.name} is blacklisted!")
        return False
    
    if comment_is_replied(post.id):
        print(f"{post.id} has already been replied to!")
        return False

    return True

def format_reply(text : str):
    reply_text = get_comment_text(text)

    if reply_text != "":
        return add_footer(reply_text)

    return reply_text

def get_comment_text(text : str):
    comment_text = ""
    for keyword in keywords:
        match = find_match(text, f" {keyword.keyword.lower()} ")

        if match == -1:
            match = find_match(text, f" {keyword.keyword.lower()}:")

        if match == -1:
            match = find_match(text, f"\"{keyword.keyword.lower()}\"")

        if match != -1:
            comment_text += f"- {keyword.comment_text}\n"
            
    return comment_text

def find_match(text, keyword):
    return text.find(keyword)

def add_footer(text: str):
    return f"{text}\n---\n\n^(_I am a bot. | DM for inquiries/feedback/opt-out._)"

