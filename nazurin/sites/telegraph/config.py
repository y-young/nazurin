from nazurin.config import env

PRIORITY = 10
COLLECTION = "telegraph"

with env.prefixed("TELEGRAPH_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Telegraph/{archive_name}")
