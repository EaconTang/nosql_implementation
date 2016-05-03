# -*- coding: utf-8 -*-
"""
abstract interface to key/value store
"""
from refer import ValueRef

class LogicalBase(object):
    """
    provide API for logical updates(like get,set...) and defers to a concrete subclass;
    also manage storage locking and dereferencing internal nodes
    """
    node_ref_class = None
    # By default, values are stored by ValueRef which expects bytes as values (to be passed directly to Storage).
    # The binary tree nodes themselves are just a sublcass of ValueRef.
    # Storing richer data via json or msgpack is a matter of writing your own and setting it as the value_ref_class.
    # BinaryNodeRef is an example of using pickle to serialise data.
    value_ref_class = ValueRef

    def __init__(self, storage):
        self._storage = storage
        self._refresh_tree_ref()

    def _refresh_tree_ref(self):
        """
        reset the tree's view of the data with what is currently on disk,
        allowing us to perform a completely up-to-date read
        """
        self._tree_ref = self.node_ref_class(
            address=self._storage.get_root_address()
        )

    def get(self, key):
        if not self._storage.locked:
            self._refresh_tree_ref()
        return self._get(self._follow(self._tree_ref), key)

    def set(self, key, value):
        if self._storage.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._insert(
            self._follow(self._tree_ref), key, self.value_ref_class(value)
        )

    def pop(self, key):
        if self._storage.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._delete(
            self._follow(self._tree_ref), key)

    def _follow(self, ref):
        return ref.get(self._storage)

    def __len__(self):
        if not self._storage.locked:
            self._refresh_tree_ref()
        root = self._follow(self._tree_ref)
        if root:
            return root.length
        else:
            return 0

    def commit(self):
        self._tree_ref.store(self._storage)
        self._storage.commit_root_address(self._tree_ref.address)

