from nazurin.config import env

PRIORITY = 8
COLLECTION = "gelbooru"

with env.prefixed("GELBOORU_"):
    API_KEY: str = env.str("API_KEY", default=None)
    USER_ID: str = env.str("USER_ID", default=None)

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Gelbooru")
        FILENAME: str = env.str("NAME", default="{id}")
