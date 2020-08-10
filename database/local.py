from tinydb import TinyDB, Query

class Local(object):
    """Local database driver using TinyDB."""

    def collection(self, key):
        self.db = TinyDB(key + '.json')
        return self

    def document(self, key):
        self._key = key
        return self

    def get(self):
        Document = Query()
        result = self.db.search(Document.key == self._key)
        if result:
            return result[0]
        else:
            return None

    def insert(self, key, data):
        if key:
            data['key'] = key
        return self.db.insert(data)

    def update(self, data):
        Document = Query()
        return self.db.update(data, Document.key == self._key)

    def delete(self):
        Document = Query()
        return self.db.remove(Document.key == self._key)
