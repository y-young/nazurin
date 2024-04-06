from nazurin.config import env

PRIORITY = 4
COLLECTION = "bilibili"

with env.prefixed("BILIBILI_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Bilibili")
    FILENAME: str = env.str(
        "NAME",
        default="{id_str}_{index} - {user[name]}({user[mid]})",
    )
