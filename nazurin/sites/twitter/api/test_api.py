import asyncio
import unittest

import pytest

from nazurin.models import Ugoira
from nazurin.utils.exceptions import NazurinError

from .syndication import SyndicationAPI
from .web import WebAPI

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class TestAPI(unittest.IsolatedAsyncioTestCase):
    syndication = SyndicationAPI()
    web = WebAPI()

    async def test_tweet_single_image(self):
        status_id = "463440424141459456"
        illust1 = await self.syndication.fetch(status_id)
        image_count = 1
        assert len(illust1.images) == image_count
        assert illust1.metadata["id_str"] == status_id

        illust2 = await self.web.fetch(status_id)
        self.assert_api_consistency(illust1, illust2)

    async def test_tweet_multiple_images(self):
        status_id = "861627479294746624"
        illust1 = await self.syndication.fetch(status_id)
        image_count = 4
        assert len(illust1.images) == image_count
        assert illust1.metadata["id_str"] == status_id

        illust2 = await self.web.fetch(status_id)
        self.assert_api_consistency(illust1, illust2)

    async def test_tweet_gif(self):
        status_id = "1453655278419779597"
        illust1 = await self.syndication.fetch(status_id)
        assert isinstance(illust1, Ugoira)
        assert illust1.metadata["id_str"] == status_id

        illust2 = await self.web.fetch(status_id)
        self.assert_api_consistency(illust1, illust2)

    async def test_tweet_not_found(self):
        status_id = "0000000000000000000"
        with pytest.raises(NazurinError):
            await self.syndication.fetch(status_id)
        with pytest.raises(NazurinError):
            await self.web.fetch(status_id)

    def assert_api_consistency(self, result1, result2):
        # We don't care about metadata since different API has different schema
        result1.metadata = result2.metadata = None
        assert result1 == result2
