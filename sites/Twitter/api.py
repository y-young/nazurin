import requests
import os
from utils import downloadImages, NazurinError

class Twitter(object):
    def getTweet(self, status_id):
        """Get a tweet from API."""
        # Old: 'https://syndication.twitter.com/tweets.json?ids='+ status_id +'&lang=en'
        api = 'https://cdn.syndication.twimg.com/tweet?id='+ str(status_id) +'&lang=en'
        response = requests.get(api)
        if response.status_code == 404:
            raise NazurinError('Tweet not found or unavailable.')
        tweet = response.json()
        return tweet

    def fetch(self, status_id):
        """Fetch & return tweet images and information."""
        tweet = self.getTweet(status_id)
        imgs = self.getImages(tweet)
        downloadImages(imgs)
        return imgs, tweet

    def getImages(self, tweet):
        """Get all images in a tweet."""
        if 'photos' not in tweet.keys():
            raise NazurinError('No photo found.')
        photos = tweet['photos']
        imgs = list()
        for photo in photos:
            filename, url = self.parseUrl(photo['url'])
            imgs.append({'name': 'twitter - ' + tweet['id_str'] + ' - ' + filename, 'url': url})
        return imgs

    def parseUrl(self, src):
        """Get filename & the url of the original image

        eg:
            src: https://pbs.twimg.com/media/DOhM30VVwAEpIHq.jpg
            return: DOhM30VVwAEpIHq.jpg, https://pbs.twimg.com/media/DOhM30VVwAEpIHq?format=jpg&name=orig

        Doc: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object
        """
        basename = os.path.basename(src)
        filename, extension = os.path.splitext(basename)
        url = 'https://pbs.twimg.com/media/' + filename + '?format=' + extension[1:] + '&name=orig'
        return basename, url