from nazurin.config import env

PRIORITY = 30
COLLECTION = "misskey"

with env.prefixed("MISSKEY_"):
    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Misskey")
        FILENAME: str = env.str(
            "NAME", default="{id}_{index} - {filename} - {user[name]}({user[username]})"
        )
