from nazurin.config import env

PRIORITY = 8
COLLECTION = "lofter"

with env.prefixed("LOFTER_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str("PATH", default="Lofter")
    FILENAME: str = env.str("NAME", default="{id}_{index} - {nickName}({blogName})")
