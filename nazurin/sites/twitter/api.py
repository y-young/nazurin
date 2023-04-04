import os
from typing import List, Tuple

from nazurin.models import Caption, File, Illust, Image, Ugoira
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from .config import DESTINATION, FILENAME


class Twitter:
    @network_retry
    async def get_tweet(self, status_id: int):
        """Get a tweet from API."""
        # Old: 'https://syndication.twitter.com/tweets.json?ids='+ status_id +'&lang=en'
        API_URL = "https://cdn.syndication.twimg.com/tweet-result"
        params = {
            "features": "tfw_tweet_edit_backend:on",
            "id": str(status_id),
            "lang": "en",
        }
        async with Request() as request:
            async with request.get(API_URL, params=params) as response:
                if response.status == 404:
                    raise NazurinError("Tweet not found or unavailable.")
                response.raise_for_status()
                tweet = await response.json()
                del tweet["__typename"]
                return tweet

    async def fetch(self, status_id: int) -> Illust:
        """Fetch & return tweet images and information."""
        tweet = await self.get_tweet(status_id)
        if "video" in tweet:
            return await self.get_video(tweet)
        imgs = self.get_images(tweet)
        caption = self.build_caption(tweet)
        return Illust(imgs, caption, tweet)

    def get_images(self, tweet) -> List[Image]:
        """Get all images in a tweet."""
        if "photos" not in tweet:
            raise NazurinError("No photo found.")
        photos = tweet["photos"]
        imgs = []
        for index, photo in enumerate(photos):
            filename, url, thumbnail = self.parse_url(photo["url"])
            destination, filename = self.get_storage_dest(filename, tweet, index)
            imgs.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                    width=photo["width"],
                    height=photo["height"],
                )
            )
        return imgs

    async def get_video(self, tweet) -> Ugoira:
        variants = tweet["mediaDetails"][0]["video_info"]["variants"]
        max_bitrate = -1
        best_variant = None

        for variant in variants:
            if variant["content_type"] != "video/mp4":
                continue
            # https://video.twimg.com/amplify_video/1625137841473982464/vid/720x954/YzLr5Rw4xODqTpkm.mp4?tag=16
            bitrate = variant["bitrate"] if "bitrate" in variant else 0
            if bitrate > max_bitrate:
                max_bitrate = variant["bitrate"]
                best_variant = variant["url"]
        if not best_variant:
            raise NazurinError("Failed to select best video variant.")

        filename = os.path.basename(best_variant.split("?")[0])
        destination, filename = self.get_storage_dest(filename, tweet)
        file = File(filename, best_variant, destination)
        async with Request() as session:
            await file.download(session)
        return Ugoira(file, self.build_caption(tweet), tweet)

    @staticmethod
    def get_storage_dest(filename: str, tweet: dict, index: int = 0) -> Tuple[str, str]:
        """
        Format destination and filename.
        """
        filename, extension = os.path.splitext(filename)
        created_at = fromisoformat(tweet["created_at"])
        context = {
            **tweet,
            # Original filename in twimg.com URL, without extension
            "filename": filename,
            # Photo index in a tweet
            "index": index,
            "created_at": created_at,
            "extension": extension,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + extension,
        )

    @staticmethod
    def build_caption(tweet) -> Caption:
        return Caption(
            {
                "url": f"https://twitter.com/{tweet['user']['screen_name']}"
                + f"/status/{tweet['id_str']}",
                "author": f"{tweet['user']['name']} #{tweet['user']['screen_name']}",
                "text": tweet["text"],
            }
        )

    @staticmethod
    def parse_url(src: str) -> Tuple[str, str, str]:
        """Get filename, original file url & thumbnail url of the original image

        eg:
        - src: 'https://pbs.twimg.com/media/DOhM30VVwAEpIHq.jpg'
        - return: 'DOhM30VVwAEpIHq.jpg',
            'https://pbs.twimg.com/media/DOhM30VVwAEpIHq?format=jpg&name=orig',
            'https://pbs.twimg.com/media/DOhM30VVwAEpIHq?format=jpg&name=large'

        Doc:
            https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object
        """
        basename = os.path.basename(src)
        filename, extension = os.path.splitext(basename)
        url = "https://pbs.twimg.com/media/" + filename + "?format=" + extension[1:]
        return basename, (url + "&name=orig"), (url + "&name=large")
