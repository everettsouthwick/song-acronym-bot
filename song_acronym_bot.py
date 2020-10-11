import modules.service as service
import praw

r = praw.Reddit("songacronymbot")

def stream():
    subreddit = r.subreddit(service.get_enabled_subreddits())
    stream = praw.models.util.stream_generator(lambda **kwargs: service.submissions_and_comments(subreddit, **kwargs))
    
    for post in stream:
        service.process_post(post)

stream()