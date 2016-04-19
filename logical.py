# -*- coding: utf-8 -*-
"""
abstract interface to key/value store
"""


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


class ValueRef(object):
    """
    python object that refers to a binary blob stored in database
    """

    def __init__(self, referent=None, address=0):
        self._referent = referent
        self._address = address

    def prepare_to_store(self, storage):
        pass

    def get(self, storage):
        if self._referent is None and self._address:
            self._referent = self.string_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        """
        serialise this node and save its storage address
        :param storage:
        :return:
        """
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_string(self._referent))

    @staticmethod
    def referent_to_string(referent):
        return referent.encode('utf-8')

    @staticmethod
    def string_to_referent(string):
        return string.decode('utf-8')

    @property
    def address(self):
        return self._address
