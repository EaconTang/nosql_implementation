# -*- coding: utf-8 -*-
class DBException(Exception):
    """
    """

class DBStandarError(DBException):
    """

    """

class DBFileNotExistError(DBStandarError):
    """

    """

class ValueRefLengthError(DBStandarError):
    """

    """

class BinaryTreeKeyError(KeyError):
    """

    """