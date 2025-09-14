from __future__ import annotations

import json
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from typing import TYPE_CHECKING, ClassVar
from urllib.parse import urlparse

import bs4
from x_client_transaction import ClientTransaction

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from http.cookies import SimpleCookie

    from aiohttp import ClientResponse

from nazurin.models import Illust, Image
from nazurin.utils.decorators import Cache, network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromasctimeformat
from nazurin.utils.logging import logger
from nazurin.utils.network import Request

from ..config import AUTH_TOKEN
from .base import BaseAPI


class Headers:
    AUTHORIZATION = "Authorization"
    GUEST_TOKEN = "x-guest-token"
    CSRF_TOKEN = "x-csrf-token"
    AUTH_TYPE = "x-twitter-auth-type"
    RATE_LIMIT_LIMIT = "x-rate-limit-limit"
    RATE_LIMIT_RESET = "x-rate-limit-reset"
    CLIENT_TRANSACTION_ID = "x-client-transaction-id"
    REFERER = "referer"


class AuthorizationToken:
    # From Fritter
    GUEST = (
        "Bearer AAAAAAAAAAAAAAAAAAAAAGHtAgAAAAAA%2Bx7ILXNILCqk"
        "SGIzy6faIHZ9s3Q%3DQy97w6SIrzE7lQwPJEYQBsArEE2fC25caFwRBvAGi456G09vGR"
    )
    # Official
    LOGGED_IN = (
        "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH"
        "5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )


class TweetDetailAPI:
    # From Fritter
    GUEST = "3XDB26fBve-MmjHaWTUZxA/TweetDetail"
    LOGGED_IN = "_8aYOgEDz35BrBcBal1-_w/TweetDetail"


ERROR_MESSAGES = {
    "NsfwLoggedOut": "NSFW tweet, please log in",
    "Protected": "Protected tweet, you may try logging in if you have access",
    "Suspended": "This account has been suspended",
}

BASE_URL = "https://x.com"


class WebAPI(BaseAPI):
    auth_token = AUTH_TOKEN
    headers: ClassVar[dict[str, str]] = {
        "Authorization": AuthorizationToken.GUEST,
        Headers.REFERER: BASE_URL,
        Headers.GUEST_TOKEN: "",
        "x-twitter-client-language": "en",
        "x-twitter-active-user": "yes",
    }
    variables: ClassVar[dict[str, bool]] = {
        "with_rux_injections": False,
        "includePromotedContent": False,
        "withCommunity": True,
        "withQuickPromoteEligibilityTweetFields": False,
        "withBirdwatchNotes": False,
        "withVoice": True,
    }
    features: ClassVar[dict[str, bool]] = {
        "rweb_video_screen_enabled": False,
        "profile_label_improvements_pcf_label_in_post_enabled": True,
        "rweb_tipjar_consumption_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "premium_content_api_read_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
        "responsive_web_grok_analyze_post_followups_enabled": True,
        "responsive_web_jetfuel_frame": False,
        "responsive_web_grok_share_attachment_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "responsive_web_grok_show_grok_translated_post": False,
        "responsive_web_grok_analysis_button_from_backend": True,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_grok_image_annotation_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    }

    def __init__(self):
        csrf_token = secrets.token_hex(16)
        WebAPI.cookies = {"ct0": csrf_token}
        WebAPI.headers[Headers.CSRF_TOKEN] = csrf_token

        if WebAPI.auth_token:
            WebAPI.headers[Headers.AUTH_TYPE] = "OAuth2Session"
            WebAPI.cookies["auth_token"] = WebAPI.auth_token

    async def fetch(self, status_id: int) -> Illust:
        """Fetch & return tweet images and information."""

        if AUTH_TOKEN:
            tweet = await self.tweet_detail(status_id)
        else:
            tweet = await self.tweet_result_by_rest_id(status_id)

        if "extended_entities" not in tweet:
            raise NazurinError("No photo found.")
        media = tweet["extended_entities"]["media"]
        imgs: list[Image] = []
        for medium in media:
            if medium["type"] == "photo":
                index = len(imgs)
                original_info = medium["original_info"]
                imgs.append(
                    BaseAPI.parse_photo(
                        tweet,
                        {
                            "url": medium["media_url_https"],
                            "width": original_info["width"],
                            "height": original_info["height"],
                        },
                        index,
                    ),
                )
            else:
                # video or animated_gif
                variants = medium["video_info"]["variants"]
                return await self.get_best_video(tweet, variants)
        if len(imgs) == 0:
            raise NazurinError("No photo found.")
        caption = self.build_caption(tweet)
        return Illust(status_id, imgs, caption, tweet)

    async def tweet_detail(self, tweet_id: str):
        logger.info("Fetching tweet {} from web API /TweetDetail", tweet_id)
        api = f"{BASE_URL}/i/api/graphql/" + (
            TweetDetailAPI.LOGGED_IN if AUTH_TOKEN else TweetDetailAPI.GUEST
        )
        self.headers.update(
            {
                Headers.AUTHORIZATION: (
                    AuthorizationToken.LOGGED_IN
                    if AUTH_TOKEN
                    else AuthorizationToken.GUEST
                ),
            },
        )
        variables = WebAPI.variables
        variables.update({"focalTweetId": tweet_id})
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(WebAPI.features),
        }
        await self._require_auth()
        response = await self._json_request("GET", api, params=params)
        try:
            return self._process_response(response, tweet_id)
        except KeyError as error:
            msg = "Failed to parse response:"
            logger.error("{} {}", msg, error)
            logger.info("{}", response)
            raise NazurinError(f"{msg} {error}") from error

    async def tweet_result_by_rest_id(self, tweet_id: str):
        logger.info("Fetching tweet {} from web API /TweetResultByRestId", tweet_id)
        api = "https://api.x.com/graphql/zAz9764BcLZOJ0JU2wrd1A/TweetResultByRestId"
        variables = WebAPI.variables
        variables.update({"tweetId": tweet_id})
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(WebAPI.features),
        }
        # This API uses the same token as logged-in TweetDetail
        self.headers.update({Headers.AUTHORIZATION: AuthorizationToken.LOGGED_IN})
        await self._require_auth()
        response = await self._json_request("GET", api, params=params)
        try:
            tweet_result = response["data"]["tweetResult"]
            if "result" not in tweet_result:
                logger.warning("Empty tweet result: {}", response)
                raise NazurinError("Tweet not found.")
            return WebAPI.normalize_tweet(tweet_result["result"])
        except KeyError as error:
            msg = "Failed to parse response:"
            logger.error("{} {}", msg, error)
            logger.info("{}", response)
            raise NazurinError(f"{msg} {error}") from error

    async def _require_auth(self):
        if not WebAPI.headers.get(Headers.AUTH_TYPE):
            await self._get_guest_token()

    @network_retry
    async def _json_request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        *,
        require_tid=True,
        **kwargs,
    ):
        if not headers:
            headers = {}
        if require_tid:
            tid = await self._generate_transaction_id(url)
            headers[Headers.CLIENT_TRANSACTION_ID] = tid
        headers.update(WebAPI.headers)

        async with self._raw_request(method, url, headers, **kwargs) as response:
            if not response.ok:
                result = await response.text()
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise NazurinError(
                        f"Failed to authenticate Twitter web API: {result}, "
                        "try updating auth token.",
                    )
                if response.status == HTTPStatus.NOT_FOUND:
                    raise NazurinError(
                        "Twitter API returned status 404, this could be "
                        "due to a temporary error or an upstream API change. "
                        "Please check if the tweet exists, clear cache and try again, "
                        "if the tweet exists but the error persists, "
                        "raise an issue on GitHub."
                    )
                raise NazurinError(
                    f"Twitter web API error ({response.status}, {url=}): {result}"
                )
            result = await response.json()
            return result

    @staticmethod
    @asynccontextmanager
    async def _raw_request(
        method: str, url: str, headers: dict | None = None, **kwargs
    ) -> AsyncGenerator[ClientResponse, None]:
        logger.debug(
            "Sending raw requests: url={}, headers={}, cookies={}",
            url,
            headers,
            WebAPI.cookies,
        )

        async with (
            Request(
                headers=headers,
                cookies=WebAPI.cookies,
                # Twitter homepage has long content-security-policy header
                max_field_size=1024 * 48,
            ) as request,
            request.request(method, url, **kwargs) as response,
        ):
            logger.debug(
                "Response status={}, headers={}, cookies={}",
                response.status,
                response.headers,
                response.cookies,
            )
            if not response.ok:
                result = await response.text()
                logger.error("Web API Error: {}, {}", response.status, result)
                if response.status == HTTPStatus.TOO_MANY_REQUESTS:
                    headers = response.headers
                    detail = ""
                    if (
                        Headers.RATE_LIMIT_LIMIT in headers
                        and Headers.RATE_LIMIT_RESET in headers
                    ):
                        rate_limit = int(headers[Headers.RATE_LIMIT_LIMIT])
                        reset_time = int(headers[Headers.RATE_LIMIT_RESET])
                        logger.error(
                            "Rate limited, limit: {}, reset: {}",
                            rate_limit,
                            reset_time,
                        )
                        reset_time = datetime.fromtimestamp(
                            reset_time,
                            tz=timezone.utc,
                        )
                        detail = f"Rate limit: {rate_limit}, Reset time: {reset_time}"
                    raise NazurinError(
                        "Hit API rate limit, please try again later. " + detail,
                    )
            WebAPI._update_cookies(response.cookies)
            yield response

    @staticmethod
    def _update_cookies(cookies: SimpleCookie):
        WebAPI.cookies.update(cookies)
        # CSRF token is updated after each request
        if csrf_token := cookies.get("ct0"):
            if csrf_token.value:
                WebAPI.headers[Headers.CSRF_TOKEN] = csrf_token.value
            else:
                del WebAPI.headers[Headers.CSRF_TOKEN]

    @Cache.lru(ttl=3600)
    async def _get_guest_token(self):
        logger.info("Fetching guest token")
        WebAPI.headers[Headers.GUEST_TOKEN] = ""
        WebAPI.cookies["gt"] = ""
        api = "https://api.twitter.com/1.1/guest/activate.json"
        response = await self._json_request("POST", api, require_tid=False)
        token = response.get("guest_token")
        if not token:
            raise NazurinError(f"Failed to get guest token: {response}")
        WebAPI.headers[Headers.GUEST_TOKEN] = token
        WebAPI.cookies["gt"] = token
        logger.info("Fetched guest token: {}", token)
        return token

    def _process_response(self, response: dict, tweet_id: str):
        if "errors" in response:
            logger.error(response)
            raise NazurinError(
                "\n".join([error["message"] for error in response["errors"]]),
            )

        instructions = response["data"]["threaded_conversation_with_injections_v2"][
            "instructions"
        ]
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries = instruction["entries"]
                break
        # Find tweet in timeline instructions
        tweet = None
        for entry in entries:
            if entry["entryId"] == f"tweet-{tweet_id}":
                tweet = entry["content"]["itemContent"]["tweet_results"]
                if "result" not in tweet:
                    logger.warning("Empty tweet result: {}", response)
                    raise NazurinError(
                        "Tweet result is empty, maybe it's a sensitive tweet "
                        "or the author limited visibility, "
                        "you may try setting an AUTH_TOKEN.",
                    )
                tweet = tweet["result"]
                break

        if not tweet:
            error = "Failed to find tweet detail in response"
            logger.error(error)
            logger.info("{}", response)
            raise NazurinError(error)

        # Check if tweet is available
        typename = tweet.get("__typename")
        if typename == "TweetTombstone":
            tombstone = tweet["tombstone"]["text"]
            logger.error("Encountered tweet tombstone: {}", tombstone)
            text = tombstone["text"]
            if text.startswith("Age-restricted"):
                raise NazurinError(
                    "Age-restricted adult content. Please set Twitter auth token.",
                )
            raise NazurinError(text)

        # When using auth token, and e.g. the user limited who can reply,
        # the result is not a direct tweet type, the real tweet is nested.
        if typename == "TweetWithVisibilityResults" or tweet.get("tweet"):
            tweet = tweet["tweet"]
        tweet = WebAPI.normalize_tweet(tweet)
        # Return original tweet if it's a retweet
        retweet_original = tweet.get("retweeted_status_result")
        if retweet_original:
            tweet = WebAPI.normalize_tweet(retweet_original["result"])
            logger.info("Is a retweet, original tweet: {}", tweet["id_str"])
        return tweet

    @staticmethod
    def normalize_tweet(data: dict):
        """
        Transform tweet object from API to a normalized schema.
        """

        if data.get("__typename") == "TweetUnavailable":
            reason = WebAPI.error_message_by_reason(data.get("reason"))
            raise NazurinError(f"Tweet is unavailable, reason: {reason}.")
        tweet = data["legacy"]
        tweet.update(
            {
                "created_at": fromasctimeformat(tweet["created_at"]).isoformat(),
                "user": WebAPI.normalize_user(data["core"]["user_results"]["result"]),
                "text": tweet["full_text"],
            },
        )
        del tweet["full_text"]
        return tweet

    @staticmethod
    def normalize_user(data: dict):
        """
        Transform user object from API to a normalized schema.
        """

        user = data["legacy"]
        user.update(
            {
                "id_str": data["rest_id"],
                "created_at": fromasctimeformat(user["created_at"]).isoformat(),
                "is_blue_verified": data["is_blue_verified"],
            },
        )
        return user

    @staticmethod
    def error_message_by_reason(reason: str):
        if reason in ERROR_MESSAGES:
            return ERROR_MESSAGES[reason]
        return reason

    @network_retry
    @Cache.lru(ttl=86400)
    async def _get_home_page_source(self) -> bs4.BeautifulSoup:
        logger.info("Fetching Twitter home page source")
        async with self._raw_request(
            "GET", f"{BASE_URL}/home" if AUTH_TOKEN else f"{BASE_URL}/"
        ) as response:
            response.raise_for_status()
            source = await response.text()
        return bs4.BeautifulSoup(source, "html.parser")

    async def _generate_transaction_id(self, url: str, method: str = "GET") -> str:
        path = urlparse(url).path
        method = method.upper()
        try:
            home_page_source = await self._get_home_page_source()
            tid_generator = ClientTransaction(home_page_source)
            return tid_generator.generate_transaction_id(method, path)
        except Exception as error:
            message = f"Failed to generate Twitter client transaction ID: {error}"
            logger.error(message)
            raise NazurinError(message) from error
