from nazurin.config import env

PRIORITY = 15
COLLECTIONS = {
    "yande.re": "yandere",
    "konachan.com": "konachan",
    "lolibooru.moe": "lolibooru",
}

with env.prefixed("MOEBOORU_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="{site_name}")
    FILENAME: str = env.str("NAME", default="{filename}")
