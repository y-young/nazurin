from nazurin.config import env

PRIORITY = 30
COLLECTION = "danbooru"

with env.prefixed("DANBOORU_"):
    USER_ID: int | None = env.int("USER_ID", default=None)

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Danbooru")
        FILENAME: str = env.str("NAME", default="{id} - {filename}")

UA = f"Nazurin (user #{USER_ID})" if USER_ID is not None else "Nazurin"
USER_ID_HINT = (
    "Danbooru requires a user ID in User-Agent, "
    "try setting DANBOORU_USER_ID to your user ID."
)
