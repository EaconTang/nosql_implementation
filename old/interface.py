# -*- coding: utf-8 -*-
from binary_tree import BinaryTree
from physical import Storage

import os


class DBDB(object):
    """
    implements the python dictionary API using the concrete BinaryTree implementation
    """
    def __init__(self, f):
        self._storage = Storage(f)
        # Data stores tend to use more complex types of search trees such as
        # B-trees, B+ trees, and others to improve the performance.
        self._tree = BinaryTree(self._storage)

    def _assert_not_closed(self):
        if self._storage.closed:
            raise ValueError('Database closed!')

    def commit(self):
        self._assert_not_closed()
        self._tree.commit()

    def close(self):
        self._storage.close()

    def __getitem__(self, key):
        self._assert_not_closed()
        return self._tree.get(key)

    def __setitem__(self, key, value):
        self._assert_not_closed()
        return self._tree.set(key, value)

    def __delitem__(self, key):
        self._assert_not_closed()
        return self._tree.pop(key)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __len__(self):
        return len(self._tree)


def connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)


if __name__ == '__main__':
    db = connect('test.db')
    db['foo'] = 'bar'
    db['foo1'] = 'bar1'
    db['foo2'] = 'bar2'

    for i in range(1000):
        key = 'foo' + str(i)
        val = 'bar' + str(i)
        db[key] = val
        print 'saved[key:value]: ', key, ':', val

    for i in range(1000):
        key = 'foo' + str(i)
        print key, ':', db[key]


