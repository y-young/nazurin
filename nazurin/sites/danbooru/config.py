from nazurin.config import env

PRIORITY = 30
COLLECTION = "danbooru"

with env.prefixed("DANBOORU_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Danbooru")
    FILENAME: str = env.str("NAME", default="{id} - {filename}")
