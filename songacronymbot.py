from modules.models import Blacklist, Comment, Keyword
import modules.repository as Repo
import praw
import time

# Initialize Reddit instance.
reddit = praw.Reddit("bot1", user_agent="script:songacronymbot:v1.0 (by u/everdoot)")

# Initialize list of keywords we are looking for.
keywords = Repo.get_all_keywords()

def should_comment(comment : praw.models.Comment):
    if comment.author.name == "songacronymbot":
        print("This is your own comment!")
        return False

    if time.time() - comment.created_utc > 600:
        print("Comment is greater than 10 minutes old!")
        return False

    if Repo.author_is_blacklisted(comment.author.name):
        print(f"{comment.author.name} is blacklisted!")
        return False
    
    if Repo.comment_is_replied(comment.id):
        print(f"{comment.id} has already been replied to!")
        return False

    return True

def format_reply(body : str):
    reply_text = ""
    for keyword in keywords:
        match = body.find(f" {keyword.keyword.lower()} ")

        if match != -1:
            if reply_text == "":
                reply_text = f"> {keyword.comment_text}"
            else:
                reply_text = f"{reply_text}\n> {keyword.comment_text}"

    return add_footer(reply_text)

def add_footer(reply_text: str):
    if reply_text == "":
        return reply_text

    return f"{reply_text}\n___\n^(I am a bot. | DM to be removed from automatic replies.)"

def crawl():
    for comment in reddit.subreddit('taylorswift').stream.comments():
        comment_id = comment.id
        comment_body = comment.body.lower()

        if not should_comment(comment):
            continue

        reply_text = format_reply(comment_body)

        if reply_text != "":
            try:
                print("I replied to '" + comment_body + "' with " + reply_text)
                comment.reply(reply_text)
                Repo.add_comment(comment_id, 1)
                time.sleep(601)
            except:
                print("Error!")
                break

crawl()