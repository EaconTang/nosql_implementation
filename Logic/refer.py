# -*- coding: utf-8 -*-
"""
refer point to real value
"""
import pickle
from tree import BinaryNode
from exception import *

class ValueRef(object):
    """
    python object that refers to a binary blob stored in database
    """
    def __init__(self, refer_to=None, address=0):
        self._refer = refer_to
        self._address = address

    def prepare_to_store(self, storage):
        pass

    def get(self, storage):
        if self._refer is None and self._address:
            self._refer = self.string_to_refer(storage.read(self._address))
        return self._refer

    def store(self, storage):
        """
        serialise this node and save its storage address
        :param storage:
        :return:
        """
        if self._refer is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.refer_to_string(self._refer))

    def string_to_refer(self, string):
        raise NotImplementedError

    def refer_to_string(self, refer):
        raise NotImplementedError

    def address(self):
        return self._address


class StringValueRef(ValueRef):
    """

    """
    def string_to_refer(self, string):
        return string.decode('utf-8')

    def refer_to_string(self, refer):
        return refer.encode('utf-8')

class BinaryNodeRef(ValueRef):
    """
    a ValueRef which could serialise and deserialise a binary node
    """
    def prepare_to_store(self, storage):
        if self._refer:
            self._refer.store_refs(storage)

    def refer_to_string(self, refer):
        """
        serialise(pickle) node by creating a bytestring
        :param refer:
        :return:
        """
        _node_dict = {
            'left': refer.left_ref.address,
            'key': refer.key,
            'value': refer.value_ref.address,
            'right': refer.right_ref.address,
            'length': refer.length,
        }

        return pickle.dumps(_node_dict)

    def string_to_refer(self, string):
        node_dict = pickle.loads(string)
        _node = BinaryNode(
            left_ref=BinaryNodeRef(address=node_dict['left']),
            key=node_dict['key'],
            value_ref=node_dict['value'],
            right_ref=BinaryNodeRef(address=node_dict['right']),
            length=node_dict['length'],
        )
        return _node

    @property
    def length(self):
        if self._refer is None and self._address:
            raise ValueRefLengthError("No length for exist binary node!")
        if self._refer:
            return self._refer.length
        else:
            raise ValueRefLengthError("No length for non-exist binary node!")