from inspect import getfullargspec
from types import LambdaType, FunctionType

from sqldirect.errors import SQLDirectError

def record_factory(types, merge=None, switch=None):
    if types is None:
        return Dictionary()
    if isinstance(types, list) and switch is None:
        return Types([record_factory(t) for t in types], merge)
    if isinstance(types, list) and switch is not None:
        return PolymorphicObject(switch, types)
    elif types == dict:
        return Dictionary()
    elif isinstance(types, FunctionType) or  isinstance(types, LambdaType):
        #ignore merge
        return Function(types)
    else:
        #must be a custom type
        return Object(types)

class Types(object):
    def __init__(self, types, relations=None):
        self._types = types if isinstance(types, list) else [types]
        #todo: check relations has num arguments == len(types)
        if relations is not None:
            if len(getfullargspec(relations).args) != len(types):
                raise Exception("Result types are not same number of realtion function arguments")
        self._relations = relations

    def map(self, dbrecord):
        mapped = [t.map(dbrecord) for t in self._types]
        if self._relations is not None:
            return self._relations(mapped[0], mapped[1])
        else:
            return mapped[0]

class Type(object):
    def __init__(self):
        pass

class Dictionary(Type):
    def __init__(self, map=None):
        self._map = map

    def map(self, dbrecord):
        return dict(dbrecord)


class Object(Type):
    def __init__(self, type_, extra_fields=None):
        self._type = type_
        self._extra_fields = extra_fields

    def typename(self):
        return self._type.__name__

    def map(self, dbrecord):
        if self._extra_fields is not None:
            dbrecord = {**dbrecord, **self._extra_fields}

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
        else:
            raise SQLDirectError("Cannot create object with more than 7 args in ctor")

    def _create1(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]])

    def _create2(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]])

    def _create3(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]], dbrecord[ctor_args[3]])

    def _create4(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]], dbrecord[ctor_args[3]], dbrecord[ctor_args[4]])

    def _create5(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]], dbrecord[ctor_args[3]], dbrecord[ctor_args[4]], dbrecord[ctor_args[5]])

    def _create6(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]], dbrecord[ctor_args[3]], dbrecord[ctor_args[4]], dbrecord[ctor_args[5]], dbrecord[ctor_args[6]])

    def _create7(self, dbrecord, ctor_args):
        return self._type(dbrecord[ctor_args[1]], dbrecord[ctor_args[2]], dbrecord[ctor_args[3]], dbrecord[ctor_args[4]], dbrecord[ctor_args[5]], dbrecord[ctor_args[6]], dbrecord[ctor_args[7]])


class Function(Type):
    def __init__(self, func):
        self._func = func

    def map(self, dbrecord):
        return self._func(dbrecord)


class PolymorphicObject(Type):
    def __init__(self, type_switch, types):
        self._type_switch = type_switch
        self._objects = {t.typename(): t for t in [record_factory(t) for t in types]}
        pass

    def map(self, dbrecord):
        return self._objects[dbrecord[self._type_switch]].map(dbrecord)



