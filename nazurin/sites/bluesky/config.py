from nazurin.config import env

PRIORITY = 10
COLLECTION = "bluesky"

with env.prefixed("BLUESKY_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Bluesky")
    FILENAME: str = env.str(
        "NAME",
        default="{rkey}_{index} - {user[display_name]}({user[handle]})",
    )
