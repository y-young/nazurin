from http import HTTPStatus
from typing import List

from nazurin.models import Illust, Image, Ugoira
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.logging import logger

from .base import BaseAPI


class SyndicationAPI(BaseAPI):
    """Public API from publish.twitter.com"""

    API_URL = "https://cdn.syndication.twimg.com/tweet-result"

    @network_retry
    async def get_tweet(self, status_id: int):
        """Get a tweet from API."""
        logger.info("Fetching tweet {} from syndication API", status_id)
        params = {
            "features": "tfw_tweet_edit_backend:on",
            "id": str(status_id),
            "lang": "en",
        }
        async with Request() as request, request.get(
            self.API_URL,
            params=params,
        ) as response:
            if response.status == HTTPStatus.NOT_FOUND:
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
        return Illust(status_id, imgs, caption, tweet)

    def get_images(self, tweet) -> List[Image]:
        """Get all images in a tweet."""
        if "photos" not in tweet:
            raise NazurinError("No photo found.")
        photos = tweet["photos"]
        imgs = []
        for index, photo in enumerate(photos):
            imgs.append(BaseAPI.parse_photo(tweet, photo, index))
        return imgs

    async def get_video(self, tweet) -> Ugoira:
        variants = tweet["mediaDetails"][0]["video_info"]["variants"]
        return await self.get_best_video(tweet, variants)
