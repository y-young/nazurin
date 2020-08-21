from database import Database
from time import time
from .api import Twitter
from .config import TWITTER_COLLECTION

PRIORITY = 5
patterns = [
    # https://twitter.com/i/web/status/1234567890123456789
    # https://twitter.com/abcdefg/status/1234567890123456789
    # https://mobile.twitter.com/abcdefg/status/1234567890123456789
    r'(?:mobile\.)?twitter\.com/[^.]+/status/(\d+)'
]

def handle(match, **kwargs):
    status_id = match.group(1)
    db = Database().driver()
    collection = db.collection(TWITTER_COLLECTION)
    imgs, tweet = Twitter().fetch(status_id)
    tweet['collected_at'] = time()
    collection.insert(status_id, tweet)
    return imgs