class Caption(dict):
    @property
    def text(self) -> str:
        caption = str()
        for key, value in self.items():
            if not value:
                continue
            caption += str(key) + ': ' + str(value) + '\n'
        return caption
