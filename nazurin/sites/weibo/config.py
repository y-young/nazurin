from nazurin.config import env

PRIORITY = 5
COLLECTION = "weibo"

with env.prefixed("WEIBO_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Weibo")
    FILENAME: str = env.str(
        "NAME",
        default="{mid}_{index} - {user[screen_name]}({user[id]})",
    )
