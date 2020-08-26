from database import Database
from time import time
from .api import Twitter
from .config import COLLECTION

patterns = [
    # https://twitter.com/i/web/status/1234567890123456789
    # https://twitter.com/abcdefg/status/1234567890123456789
    # https://www.twitter.com/abcdefg/status/1234567890123456789
    # https://mobile.twitter.com/abcdefg/status/1234567890123456789
    r'(?:mobile\.|www\.)?twitter\.com/[^.]+/status/(\d+)'
]

def handle(match, **kwargs):
    status_id = match.group(1)
    db = Database().driver()
    collection = db.collection(COLLECTION)
    imgs, tweet = Twitter().fetch(status_id)
    tweet['collected_at'] = time()
    collection.insert(status_id, tweet)
    return imgs