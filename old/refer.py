# -*- coding: utf-8 -*-
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


class BinaryNodeRef(ValueRef):
    """
    as a specialised ValueRef which knows how to serialise and deserialise a BinaryNode
    """
    def prepare_to_store(self, storage):
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_string(referent):
        """
        serialise it by creating a bytestring representing this node
        :param referent:
        :return:
        """
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'length': referent.length,
        })

    @staticmethod
    def string_to_referent(string):
        d = pickle.loads(string)
        return BinaryNode(
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
            d['length'],
        )

    @property
    def length(self):
        if self._referent is None and self._address:
            raise RuntimeError('Asking for BinaryNodeRef length of unloaded node')
        if self._referent:
            return self._referent.length
        else:
            return 0
