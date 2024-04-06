from nazurin.config import env

PRIORITY = 10
COLLECTION = "deviantart"

with env.prefixed("DEVIANT_ART_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="DeviantArt")
    FILENAME: str = env.str("NAME", default="{title} - {deviationId}")
    DOWNLOAD_FILENAME: str = env.str(
        "DOWNLOAD_NAME",
        default="{title} - {deviationId} - {prettyName}",
    )
