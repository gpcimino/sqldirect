class Dictionary(object):
    def __init__(self, key_map=None):
        self._key_map = key_map

    def map(self, dbrecord):
        if self._key_map is None:
            # todo: check if dbrecord is already a dict
            return dict(dbrecord)
        else:
            # rename keys using key map
            d = dict(dbrecord)
            for k in self._key_map:
                d[self._key_map[k]] = d.pop(k)  # why pop?
            return d
