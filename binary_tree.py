# -*- coding: utf-8 -*-
"""
concrete implementation of a binary tree
"""
import pickle
from logical import ValueRef, LogicalBase


class BinaryTree(LogicalBase):
    """
    represents an immutable tree;
    updates are performed by returning a new tree which shares common structure with the old one
    """
    node_ref_class = BinaryNodeRef

    def _get(self, node, key):
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif key > node.key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError

    def _insert(self, node, key, value_ref):
        """
        inserting or updating the tree doesn't mutate any nodes, because _insert() returns a new tree
        """
        if node is None:
            new_node = BinaryNode(
                self.node_ref_class(), key, value_ref, self.node_ref_class(), 1
            )
        elif key < node.key:
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref
                )
            )
        elif key > node.key:
            new_node = BinaryNode.from_node(
                node,
                right_ref = self._insert(
                    self._follow(node.right_ref), key, value_ref
                )
            )
        else:
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return self.node_ref_class(referent=new_node)

    def _delete(self, node, key):
        """
        :param node:
        :param key:
        :return:
        """
        if node is None:
            raise KeyError
        elif key < node.key:
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._delete(self._follow(node.left_ref), key)
            )
        elif key > node.key:
            new_node = BinaryNode.from_node(
                node,
                right_ref=self._delete(self._follow(node.right_ref), key)
            )
        else:
            left = self._follow(node.left_ref)
            right = self.__follow(node.right_ref)
            if left and right:
                replacement = self._find_max(left)
                left_ref = self._delete(self._follow(node.left_ref), replacement.key)
                new_node = BinaryNode(
                    left_ref,
                    replacement.key,
                    replacement.value_ref,
                    node.right_ref,
                    left_ref.length + node.right_ref.length + 1,
                )
            elif left:
                return node.left_ref
            else:
                return node.right_ref
        return self.node_ref_class(referent=new_node)

    def _find_max(self, node):
        while True:
            next_node = self._follow(node.right_ref)
            if next_node is None:
                return node
            node = next_node


class BinaryNode(object):
    """
    implements a node in the binary tree
    """
    def __init__(self, left_ref, key, value_ref, right_ref, length):
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.length = length

    def store_refs(self, storage):
        """
        This recurses all the way down for any NodeRef which has unwritten changes (i.e., no _address).
        :param storage:
        :return:
        """
        self.value_ref.store(storage)
        self.left_ref.store(storage)
        self.right_ref.store(storage)

    @classmethod
    def from_node(cls, node, **kwargs):
        """
        :param node:
        :param kwargs:
        :return:
        """
        length = node.length
        if 'left_ref' in kwargs:
            length += kwargs['left_ref'].length - node.left_ref.length
        if 'right_ref' in kwargs:
            length += kwargs['right_ref'].length - node.right_ref.length
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            length=length,
        )


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
            'value': referent.value_reg.address,
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
