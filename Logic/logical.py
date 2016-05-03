# -*- coding: utf-8 -*-
"""
logical layer
"""
from physical import PhysicalObject
from refer import ValueRef
from tree import BinaryTree


class LogicalObject(object):
    """
    implement API for  logical updates;
    """
    node_ref = None
    value_ref = ValueRef

    def __init__(self, physical_obj):
        assert isinstance(physical_obj, PhysicalObject)
        self._physical_obj = physical_obj

    def _refresh_tree_ref(self):
        """
        ensure reading up-to-data
        :return:
        """
        self._tree_ref = self.node_ref(
            address=self._physical_obj.get_root_address(),
        )

    def get(self, key):
        if not self._physical_obj.locked:
            self._refresh_tree_ref()
        return self._get(self._follow(self._tree_ref), key)

    def set(self, key, value):
        if self._physical_obj.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._set(self._follow(self._tree_ref), key, self.value_ref(value))

    def delete(self, key):
        if self._physical_obj.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._delete(self._follow(self._tree_ref), key)


    def _follow(self, ref):
        """
        node_ref to node
        :param ref:
        :return:
        """
        return ref.get(self._physical_obj)

    def __len__(self):
        if not self._physical_obj.locked:
            self._refresh_tree_ref()
        root = self._follow(self._tree_ref)
        if root:
            return root.length
        else:
            return 0


class DBDB(object):
    """
    implement the python dictionary API using concrete BinaryTree implementation
    """
    def __init__(self, f):
        self._storage = PhysicalObject(f)
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
        return self._tree.delete(key)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __len__(self):
        return len(self._tree)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._storage.closed:
            self.close()

# def connect(dbname):
#     try:
#         f = open(dbname, 'r+b')
#     except IOError:
#         fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
#         f = os.fdopen(fd, 'r+b')
#     return DBDB(f)


