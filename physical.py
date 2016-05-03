# -*- coding: utf-8 -*-
"""
physical layer
"""
import os
import struct
import portalocker
from exception import *


class PhysicalObject(object):
    """
    append-only record storage
    """

    INTEGER_FORMAT = "!Q"  # "Q": unsigned long long; "!": network byte order
    INTEGER_LENGTH = 8
    SUPERBLOCK_SIZE = 4096

    def __init__(self, file_obj=None, fd=None, file_name=None):
        if file_obj:
            self._f = file_obj
        elif fd:
            self._f = os.fdopen(fd, 'rb+')
        elif file_name:
            self._f = open(file_name)
        else:
            raise DBFileNotExistError("No database file found.")
        self.locked = False
        self.ensure_block()

    def ensure_block(self):
        """
        ensure each block is the size of SUPERBLOCK_SIZE
        :return:
        """
        self.lock()
        self.seek_end()
        end_position = self._f.tell()
        if end_position < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_position))
        self.unlcok()

    def lock(self):
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True

    def unlcok(self):
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def seek_end(self):
        self._f.seek(0, os.SEEK_END)

    def seek_superblock(self):
        self._f.seek(0)

    def seek_to_pos(self, position):
        self._f.seek(position)

    def seek_start(self):
        self.seek_superblock()

    def bytes_to_int(self, _bytes):
        return struct.unpack(self.INTEGER_FORMAT, _bytes)[0]

    def int_to_bytes(self, _int):
        return struct.pack(self.INTEGER_FORMAT, _int)

    def read_int(self):
        return self.bytes_to_int(self._f.read(self.INTEGER_LENGTH))

    def write_int(self, _int):
        self.lock()
        self._f.write(self.int_to_bytes(_int))

    def write(self, data):
        self.lock()
        self.seek_end()
        current_position = self._f.tell()
        self.write_int(len(data))  # write data length
        self._f.write(data)  # write data
        return current_position

    def read(self, position):
        self.seek_to_pos(position)
        length = self.read_int()  # read data length
        data = self._f.read(length)  # read data
        return data

    def commit_root_address(self, root_address):
        self.lock()
        self._f.flush()
        self.seek_superblock()
        self.write_int(root_address)
        self._f.flush()
        self.unlcok()

    def get_root_address(self):
        self.seek_superblock()
        root_address = self.read_int()
        return root_address

    def close(self):
        self.unlcok()
        self._f.close()

    def closed(self):
        return self._f.closed

    def __str__(self):
        assert isinstance(self._f, file)
        return self._f.name


if __name__ == '__main__':
    p = PhysicalObject(file_name='../test.db')
    print isinstance(p.int_to_bytes(100), bytes)
    i = p.bytes_to_int(p.int_to_bytes(100))
    print i

    p.seek_end()
