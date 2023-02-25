from nazurin.config import env

PRIORITY = 9
COLLECTION = "wallhaven"

with env.prefixed("WALLHAVEN_"):
    API_KEY = env.str("API_KEY", default=None)

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Wallhaven")
        FILENAME: str = env.str("NAME", default="{id}")
