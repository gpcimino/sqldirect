from inspect import getfullargspec

from sqldirect.errors import SQLDirectError


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
                # remove (pop) and add again with the new name
                d[self._key_map[k]] = d.pop(k)
            return d


class Integer(object):
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return int(dbrecord[0])
        else:
            return int(dbrecord[self._name])


class String(object):
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return str(dbrecord[0])
        else:
            return str(dbrecord[self._name])


class Float(object):
    def __init__(self, name=None):
        self._name = name

    def map(self, dbrecord):
        if self._name is None:
            return float(dbrecord[0])
        else:
            return float(dbrecord[self._name])


class Type(object):
    def __init__(self, type_, extra_fields=None):
        self._type = type_
        self._extra_fields = extra_fields

    def typename(self):
        return self._type.__name__

    def map(self, dbrecord):
        if self._extra_fields is not None:
            # when support of py3.4 will be dropped, use the one-line below
            # dbrecord = {**dbrecord, **self._extra_fields}
            tmp = dict(dbrecord).copy()
            tmp.update(self._extra_fields)
            dbrecord = tmp
        signature = getfullargspec(self._type.__init__)
        if len(signature.args) == 2:
            return self._create1(dbrecord, signature.args)
        elif len(signature.args) == 3:
            return self._create2(dbrecord, signature.args)
        elif len(signature.args) == 4:
            return self._create3(dbrecord, signature.args)
        elif len(signature.args) == 5:
            return self._create4(dbrecord, signature.args)
        elif len(signature.args) == 6:
            return self._create5(dbrecord, signature.args)
        elif len(signature.args) == 7:
            return self._create6(dbrecord, signature.args)
        elif len(signature.args) == 8:
            return self._create7(dbrecord, signature.args)
        else:
            raise SQLDirectError(
                "Cannot create object with more than 8 args in ctor"
            )

    def _create1(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]])

    def _create2(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]]
        )

    def _create3(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]],
            dbrecord[ctor_args[3]]
        )

    def _create4(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]],
            dbrecord[ctor_args[3]],
            dbrecord[ctor_args[4]]
        )

    def _create5(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]],
            dbrecord[ctor_args[3]],
            dbrecord[ctor_args[4]],
            dbrecord[ctor_args[5]]
        )

    def _create6(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]],
            dbrecord[ctor_args[3]],
            dbrecord[ctor_args[4]],
            dbrecord[ctor_args[5]],
            dbrecord[ctor_args[6]]
        )

    def _create7(self, dbrecord, ctor_args):
        return self._type(
            dbrecord[ctor_args[1]],
            dbrecord[ctor_args[2]],
            dbrecord[ctor_args[3]],
            dbrecord[ctor_args[4]],
            dbrecord[ctor_args[5]],
            dbrecord[ctor_args[6]],
            dbrecord[ctor_args[7]]
        )


class Function(object):
    def __init__(self, func):
        self._func = func

    def map(self, dbrecord):
        return self._func(dbrecord)


class Composite(object):
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
        else:
            return mapped


class Polymorphic(object):
    def __init__(self, types, type_switch):
        self._type_switch = type_switch
        self._objects = {t.typename(): t for t in types}

    def map(self, dbrecord):
        return self._objects[dbrecord[self._type_switch]].map(dbrecord)
