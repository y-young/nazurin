from enum import Enum

from nazurin.config import env


class TwitterAPI(Enum):
    SYNDICATION = "syndication"
    WEB = "web"


PRIORITY = 5
COLLECTION = "twitter"

with env.prefixed("TWITTER_"):
    API: TwitterAPI = env.enum(
        "API",
        type=TwitterAPI,
        default=TwitterAPI.WEB.value,
        ignore_case=True,
    )
    # Auth token for web API
    AUTH_TOKEN: str = env.str("AUTH_TOKEN", default=None)

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Twitter")
        FILENAME: str = env.str(
            "NAME",
            default="{id_str}_{index} - {user[name]}({user[id_str]})",
        )
