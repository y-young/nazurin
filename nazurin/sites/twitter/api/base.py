import os
from typing import Tuple

from nazurin.models import Caption, File, Image, Ugoira
from nazurin.utils import Request
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from ..config import DESTINATION, FILENAME


class BaseAPI:
    @staticmethod
    def build_caption(tweet) -> Caption:
        return Caption(
            {
                "url": (
                    f"https://twitter.com/{tweet['user']['screen_name']}"
                    f"/status/{tweet['id_str']}"
                ),
                "author": f"{tweet['user']['name']} #{tweet['user']['screen_name']}",
                "text": tweet["text"],
            },
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
    async def get_best_video(tweet: dict, variants: list) -> Ugoira:
        max_bitrate = -1
        best_variant = None

        for variant in variants:
            if variant["content_type"] != "video/mp4":
                continue
            # https://video.twimg.com/amplify_video/1625137841473982464/vid/720x954/YzLr5Rw4xODqTpkm.mp4?tag=16
            bitrate = variant.get("bitrate", 0)
            if bitrate > max_bitrate:
                max_bitrate = variant["bitrate"]
                best_variant = variant["url"]
        if not best_variant:
            raise NazurinError("Failed to select best video variant.")

        filename = os.path.basename(best_variant.split("?")[0])
        destination, filename = BaseAPI.get_storage_dest(filename, tweet)
        file = File(filename, best_variant, destination)
        async with Request() as session:
            await file.download(session)
        return Ugoira(int(tweet["id_str"]), file, BaseAPI.build_caption(tweet), tweet)

    @staticmethod
    def parse_photo(tweet: dict, photo: dict, index: int):
        filename, url, thumbnail = BaseAPI.parse_url(photo["url"])
        destination, filename = BaseAPI.get_storage_dest(filename, tweet, index)
        return Image(
            filename,
            url,
            destination,
            thumbnail,
            width=photo["width"],
            height=photo["height"],
        )
