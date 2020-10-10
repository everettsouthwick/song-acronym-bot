import modules.helper as Helper
import praw

# Initialize Reddit instance.
r = praw.Reddit("songacronymbot")

def stream():
    subreddit = r.subreddit('taylorswift')
    stream = praw.models.util.stream_generator(lambda **kwargs: Helper.submissions_and_comments(subreddit, **kwargs))
    
    for post in stream:
        Helper.process_post(post)

stream()