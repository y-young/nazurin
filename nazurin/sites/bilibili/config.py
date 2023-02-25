from nazurin.config import env

PRIORITY = 4
COLLECTION = "bilibili"

with env.prefixed("BILIBILI_"):
    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Bilibili")
        FILENAME: str = env.str(
            "NAME", default="{dynamic_id_str}_{index} - {user[name]}({user[uid]})"
        )
