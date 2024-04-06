from enum import Enum

from nazurin.config import env


class PixivPrivacy(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


PRIORITY = 10

COLLECTION = "pixiv"
DOCUMENT = "pixiv"

with env.prefixed("PIXIV_"):
    REFRESH_TOKEN: str = env.str("TOKEN", default=None)

    IMG_PROXY: str = env.str("MIRROR", default="i.pximg.net")
    TRANSLATION: str = env.str("TRANSLATION", default=None)
    BOOKMARK_PRIVACY: PixivPrivacy = env.enum(
        "BOOKMARK_PRIVACY",
        type=PixivPrivacy,
        default=PixivPrivacy.PUBLIC.value,
        ignore_case=True,
    )

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Pixiv")
        FILENAME: str = env.str(
            "NAME",
            default="{filename} - {title} - {user[name]}({user[id]})",
        )

HEADERS = {"Referer": "https://app-api.pixiv.net/"}
