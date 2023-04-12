import json
import secrets
from datetime import datetime
from http.cookies import SimpleCookie
from typing import List

from nazurin.models import Illust, Image
from nazurin.utils.decorators import Cache, network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromasctimeformat
from nazurin.utils.logging import logger
from nazurin.utils.network import Request

from ..config import AUTH_TOKEN
from .base import BaseAPI


class Headers:
    GUEST_TOKEN = "x-guest-token"
    CSRF_TOKEN = "x-csrf-token"
    AUTH_TYPE = "x-twitter-auth-type"
    RATE_LIMIT_LIMIT = "x-rate-limit-limit"
    RATE_LIMIT_RESET = "x-rate-limit-reset"


class WebAPI(BaseAPI):
    auth_token = AUTH_TOKEN
    headers = {
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH"
        "5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "Origin": "https://twitter.com",
        "Referer": "https://twitter.com",
        Headers.GUEST_TOKEN: "",
        "x-twitter-client-language": "en",
        "x-twitter-active-user": "yes",
    }
    variables = {
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
    features = {
        "blue_business_profile_image_shape_enabled": False,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweetypie_unmention_optimization_enabled": True,
        "vibe_api_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": False,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": False,
        "standardized_nudges_misinfo": True,
        (
            "tweet_with_visibility_results_" "prefer_gql_limited_actions_policy_enabled"
        ): False,
        "interactive_text_enabled": True,
        "responsive_web_text_conversations_enabled": False,
        "longform_notetweets_richtext_consumption_enabled": False,
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
        tweet = await self.tweet_detail(status_id)
        if "extended_entities" not in tweet:
            raise NazurinError("No photo found.")
        media = tweet["extended_entities"]["media"]
        imgs: List[Image] = []
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
                    )
                )
            else:
                # video or animated_gif
                variants = medium["video_info"]["variants"]
                return await self.get_best_video(tweet, variants)
        if len(imgs) == 0:
            raise NazurinError("No photo found.")
        caption = self.build_caption(tweet)
        return Illust(imgs, caption, tweet)

    async def tweet_detail(self, tweet_id: str):
        logger.info("Fetching tweet {} from web API", tweet_id)
        api = "https://twitter.com/i/api/graphql/1oIoGPTOJN2mSjbbXlQifA/TweetDetail"
        variables = WebAPI.variables
        variables.update({"focalTweetId": tweet_id})
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(WebAPI.features),
        }
        await self._require_auth()
        response = await self._request("GET", api, params=params)
        try:
            return self._process_response(response)
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

        async with Request(headers=headers, cookies=WebAPI.cookies) as request:
            async with request.request(method, url, **kwargs) as response:
                result = await response.json()
                if not response.ok:
                    logger.error("Web API Error: {}, {}", response.status, result)
                    if response.status == 401:
                        raise NazurinError(
                            f"Failed to authenticate Twitter web API: {result}, "
                            "try updating auth token."
                        )
                    if response.status == 429:
                        headers = response.headers
                        logger.error(
                            "Rate limited, limit: {}, reset: {}",
                            headers[Headers.RATE_LIMIT_LIMIT],
                            headers[Headers.RATE_LIMIT_RESET],
                        )
                        reset_time = datetime.fromtimestamp(
                            headers[Headers.RATE_LIMIT_RESET]
                        )
                        raise NazurinError(
                            "Hit API rate limit, please try again later. "
                            f"Reset time: {reset_time}"
                        )
                    raise NazurinError(f"Twitter web API error: {result}")
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

    def _process_response(self, response: dict):
        if "errors" in response:
            logger.error(response)
            raise NazurinError(
                "\n".join([error["message"] for error in response["errors"]])
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
            if entry["entryId"].startswith("tweet-"):
                tweet = entry["content"]["itemContent"]["tweet_results"]["result"]
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
                    "Age-restricted adult content. Please set Twitter auth token."
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

        tweet = data["legacy"]
        tweet.update(
            {
                "created_at": fromasctimeformat(tweet["created_at"]).isoformat(),
                "user": WebAPI.normalize_user(data["core"]["user_results"]["result"]),
                "edit_control": data["edit_control"],
                "text": tweet["full_text"],
            }
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
            }
        )
        return user
