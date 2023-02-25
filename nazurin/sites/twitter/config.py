from nazurin.config import env

PRIORITY = 5
COLLECTION = "twitter"

with env.prefixed("TWITTER_"):
    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Twitter")
        FILENAME: str = env.str(
            "NAME", default="{id_str}_{index} - {user[name]}({user[id_str]})"
        )
