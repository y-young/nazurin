from nazurin.config import env

PRIORITY = 10
COLLECTION = "pawchive"

with env.prefixed("PAWCHIVE_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str(
        "PATH",
        default="Pawchive/{service}/{username} ({user})/{title} ({id})",
    )
    FILENAME: str = env.str("NAME", default="{pretty_name}")
