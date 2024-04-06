from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from typing import ClassVar

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
    LOGGED_IN = "q94uRCEn65LZThakYcPT6g/TweetDetail"


ERROR_MESSAGES = {
    "NsfwLoggedOut": "NSFW tweet, please log in",
    "Protected": "Protected tweet, you may try logging in if you have access",
    "Suspended": "This account has been suspended",
}


class WebAPI(BaseAPI):
    auth_token = AUTH_TOKEN
    headers: ClassVar[dict[str, str]] = {
        "Authorization": AuthorizationToken.GUEST,
        "Origin": "https://twitter.com",
        "Referer": "https://twitter.com",
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
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withVoice": True,
        "withV2Timeline": True,
    }
    features: ClassVar[dict[str, bool]] = {
        "blue_business_profile_image_shape_enabled": False,
        "rweb_lists_timeline_redesign_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweetypie_unmention_optimization_enabled": True,
        "vibe_api_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": False,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": False,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "interactive_text_enabled": True,
        "responsive_web_text_conversations_enabled": False,
        "longform_notetweets_richtext_consumption_enabled": False,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_media_download_video_enabled": False,
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
        logger.info("Fetching tweet {} from web API", tweet_id)
        api = "https://twitter.com/i/api/graphql/" + (
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
        response = await self._request("GET", api, params=params)
        try:
            return self._process_response(response, tweet_id)
        except KeyError as error:
            msg = "Failed to parse response:"
            logger.error("{} {}", msg, error)
            logger.info("{}", response)
            raise NazurinError(f"{msg} {error}") from error

    async def tweet_result_by_rest_id(self, tweet_id: str):
        logger.info("Fetching tweet {} from web API /TweetResultByRestId", tweet_id)
        api = (
            "https://twitter.com/i/api/graphql"
            "/0hWvDhmW8YQ-S_ib3azIrw/TweetResultByRestId"
        )
        variables = WebAPI.variables
        variables.update({"tweetId": tweet_id})
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(WebAPI.features),
        }
        # This API uses the same token as logged-in TweetDetail
        self.headers.update({Headers.AUTHORIZATION: AuthorizationToken.LOGGED_IN})
        await self._require_auth()
        response = await self._request("GET", api, params=params)
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
    async def _request(self, method, url, headers=None, **kwargs):
        if not headers:
            headers = {}
        headers.update(WebAPI.headers)

        async with Request(
            headers=headers,
            cookies=WebAPI.cookies,
        ) as request, request.request(method, url, **kwargs) as response:
            if not response.ok:
                result = await response.text()
                logger.error("Web API Error: {}, {}", response.status, result)
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise NazurinError(
                        f"Failed to authenticate Twitter web API: {result}, "
                        "try updating auth token.",
                    )
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
                raise NazurinError(f"Twitter web API error: {result}")
            result = await response.json()
            self._update_cookies(response.cookies)
            return result

    def _update_cookies(self, cookies: SimpleCookie):
        WebAPI.cookies.update(cookies)
        # CSRF token is updated after each request
        if cookies.get("ct0"):
            WebAPI.headers[Headers.CSRF_TOKEN] = cookies["ct0"].value

    @Cache.lru(ttl=3600)
    async def _get_guest_token(self):
        logger.info("Fetching guest token")
        WebAPI.headers[Headers.GUEST_TOKEN] = ""
        WebAPI.cookies["gt"] = ""
        api = "https://api.twitter.com/1.1/guest/activate.json"
        response = await self._request("POST", api)
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
