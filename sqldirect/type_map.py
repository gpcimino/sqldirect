# pylint: disable=R0903

from inspect import getfullargspec

from sqldirect.errors import SQLDirectError


class Dictionary():
    def __init__(self, key_map=None):
        self._key_map = key_map

    def map(self, dbrecord):
        if self._key_map is None:
            return dict(dbrecord)
        # rename keys using key map
        d = dict(dbrecord)
        for k in self._key_map:
            # remove (pop) and add again with the new name
            d[self._key_map[k]] = d.pop(k)
        return d


class Integer():
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return int(dbrecord[0])
        return int(dbrecord[self._name])


class String():
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return str(dbrecord[0])
        return str(dbrecord[self._name])


class Float():
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return float(dbrecord[0])
        return float(dbrecord[self._name])


class Type():
    def __init__(self, type_, extra_fields=None):
        self._type = type_
        self._extra_fields = extra_fields

    def typename(self):
        return self._type.__name__

    def map(self, dbrecord):
        # pylint: disable-msg=R0911
        # Too many return statements (7/6) (too-many-return-statements)
        if self._extra_fields is not None:
            # when support of py3.4 will be dropped, use the one-line below to merge 2 dict
            # dbrecord = {**dbrecord, **self._extra_fields}
            tmp = dict(dbrecord).copy()
            tmp.update(self._extra_fields)
            dbrecord = tmp
        signature = getfullargspec(self._type.__init__)
        # get the fields from the record accordin to the name parameters of the ctor
        # excluding the first (self) [1:]
        ctor_args = [dbrecord[a] for a in signature.args[1:]]
        return self._type(*ctor_args)

class Function():
    def __init__(self, func):
        self._func = func

    def map(self, dbrecord):
        return self._func(dbrecord)


class Composite():
    def __init__(self, types, relation=None):
        self._types = types if isinstance(types, list) else [types]
        if relation is not None:
            if len(getfullargspec(relation).args) != len(types):
                raise SQLDirectError(
                    "Result types are not same number of realtion function arguments" # noqa
                )
        self._relation = relation

    def map(self, dbrecord):
        mapped = [t.map(dbrecord) for t in self._types]
        if self._relation is not None:
            return self._relation(*mapped)
        return mapped


class Polymorphic():
    def __init__(self, types, type_switch):
        self._type_switch = type_switch
        self._objects = {t.typename(): t for t in types}

    def map(self, dbrecord):
        return self._objects[dbrecord[self._type_switch]].map(dbrecord)
