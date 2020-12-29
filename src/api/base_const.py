#! /usr/bin/python
#
# Copyright (C) 2020 paradox.ai
#
#test

__author__ = "huy.tran@paradox.ai"
__date__ = "04/06/2020 09:39"


class const(object):
    class ConstError(TypeError):
        pass  # base exception class

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const.%s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name %r is not all uppercase' % name)
        self.__dict__[name] = value
