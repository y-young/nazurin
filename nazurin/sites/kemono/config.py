from nazurin.config import env

PRIORITY = 10
COLLECTION = "kemono"

with env.prefixed("KEMONO_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str(
        "PATH",
        default="Kemono/{service}/{username} ({user})/{title} ({id})",
    )
    FILENAME: str = env.str("NAME", default="{pretty_name}")
