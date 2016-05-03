# -*- coding: utf-8 -*-
import pickle
from refer import BinaryNodeRef
from Logic import LogicalObject
from exception import *


class BinaryTree(LogicalObject):
    """
    immutable binary tree
    return a new tree after update
    """
    node_ref = BinaryNodeRef

    def _get(self, node, key):
        assert isinstance(key, str), "Key should be type string!"
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif key > node.key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise BinaryTreeKeyError("Node not exist!")

    def _set(self, node, key, value_ref):
        """
        (Recursively)if key match, update node; if not, insert new node
        inserting or updating the tree doesn't mutate any nodes,
        because _insert() returns a new tree
        :param node:
        :param key:
        :param value_ref:
        :return:
        """
        assert isinstance(key, str), "Key should be type string!"
        if node is None:
            new_node = BinaryNode(
                key=key,
                value_ref=value_ref,
                length=1,
                left_ref=self.node_ref(),
                right_ref=self.node_ref(),
            )
        elif key < node.key:
            left_ref = self._set(self._follow(node.left_ref), key, value_ref)
            new_node = BinaryNode.from_node(node, left_ref=left_ref)
        elif key > node.key:
            right_ref = self._set(self._follow(node.right_ref), key, value_ref)
            new_node = BinaryNode.from_node(node, right_ref=right_ref)
        else:
            # key match, update value_ref
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return self.node_ref(refer=new_node)

    def _delete(self, node, key):
        assert isinstance(key, str), "Key should be type string!"
        if node is None:
            raise BinaryTreeKeyError
        elif key < node.key:
            new_node = BinaryNode.from_node(node, left_ref=self._delete(self._follow(node.left_ref), key))
        elif key > node.key:
            new_node = BinaryNode.from_node(node, right_ref=self._delete(self._follow(node.right_ref), key))
        else:
            left = self._follow(node.left_ref)
            right = self._follow(node.right_ref)
            if left and right:
                replacement = self.find_max(left)
                left_ref = self._delete(self._follow(node.left_ref), replacement.key)
                new_node = BinaryNode(
                    key=replacement.key,
                    value_ref=replacement.value_ref,
                    length=left_ref.length + 1 + node.right_ref.length,
                    left_ref=left_ref,
                    right_ref=node.right_ref,
                )
            elif left:
                return node.left_ref
            elif right:
                return node.right_ref
        return self.node_ref(refer=new_node)

    def find_max(self, node):
        while True:
            right_node = self._follow(node.right_ref)
            if right_node is None:
                return node
            node = right_node

    def find_min(self, node):
        while True:
            left_node = self._follow(node.left_ref)
            if left_node is None:
                return node
            node = left_node


class BinaryNode(object):
    """
    implement a node in the binary tree, its structure as follow:
        node:
            key ->
            value_ref ->
            length ->
            left_ref -> left-child-node
            right_ref -> right-child-node
    """
    def __init__(self, key, value_ref, length, left_ref, right_ref):
        self.key = key
        self.value_ref = value_ref
        self.length = length
        self.left_ref = left_ref
        self.right_ref = right_ref

    def store_refs(self, storage):
        self.value_ref.store(storage)
        self.left_ref.store(storage)
        self.right_ref.store(storage)

    @classmethod
    def from_node(cls, node, **kwargs):
        """
        creat node from a existing node with update args
        :param node:
        :param kwargs:
        :return:
        """
        length = node.length
        if 'left_ref' in kwargs:
            length += kwargs['left_ref'].length - node.left_ref.length
        if 'right_ref' in kwargs:
            length += kwargs['right_ref'].length - node.right_ref.length
        new_node = cls(**{
            'key': kwargs.get('key', node.key),
            'value_ref': kwargs.get('value_ref', node.valuee_ref),
            'length': kwargs.get('length', node.length),
            'left_ref': kwargs.get('left_ref', node.left_ref),
            'right_ref': kwargs.get('right_ref', node.right_ref),
        })
        return new_node

