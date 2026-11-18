from nazurin.config import env

PRIORITY = 10
COLLECTION = "xfolio"

with env.prefixed("XFOLIO_"):
    SESSION: str | None = env.str("SESSION", default=None)
    BOOKMARK: bool = env.bool("BOOKMARK", default=True)
    LIKE: bool = env.bool("LIKE", default=True)

    with env.prefixed("FILE_"):
        DESTINATION: str = env.str("PATH", default="Xfolio")
        FILENAME: str = env.str(
            "NAME",
            default="{id}_{index} - {title} - {user[name]}({user[code]})",
        )
