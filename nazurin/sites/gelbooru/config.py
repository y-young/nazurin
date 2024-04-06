from nazurin.config import env

PRIORITY = 8
COLLECTION = "gelbooru"

with env.prefixed("GELBOORU_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Gelbooru")
    FILENAME: str = env.str("NAME", default="{id}")
