from nazurin.config import env

PRIORITY = 9
COLLECTION = "zerochan"

with env.prefixed("ZEROCHAN_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Zerochan")
    FILENAME: str = env.str("NAME", default="{id} - {name}")
