from nazurin.config import CAPTION_IGNORE


class Caption(dict):
    @property
    def text(self) -> str:
        caption = ""
        for key, value in self.items():
            if not value or key in CAPTION_IGNORE:
                continue
            caption += str(key) + ": " + str(value) + "\n"
        return caption
