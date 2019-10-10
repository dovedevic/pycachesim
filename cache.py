import math
import enum


class Cache:
    def __init__(self, addressspace, size, associativity, blocksize, policy):
        self._addressspace = addressspace.value
        self._size = size
        self._associativity = associativity
        self._blocksize = blocksize
        self._blocks = size // blocksize
        self._sets = self._blocks // associativity

        self._offset_bits = int(math.log(self._blocksize, 2))
        self._index_bits = int(math.log(self._sets, 2))
        self._tag_bits = int(math.log(addressspace.value + 1, 2)) - self._offset_bits - self._index_bits

        self._policy = policy

        self._cache = dict()
        for cache_set in range(0, self._sets):
            self._cache[cache_set] = [Block(self._blocksize, 0, 0, 0) for i in range(associativity)]

    def _touch(self, block):
        """
        Touch a block in this cache to update the policy managing this item
        :param block:
        :return hit:
        """
        return False

    def get(self, block):
        """
        Access the cache and attempt to get a block
        :param block:
        :return hit:
        """
        return None

    def put(self, block):
        """
        Put the following block into the cache. If not space is present, use the policy to evict and return the eviction
        :param block:
        :return replacement:
        """
        return None


class Block:
    def __init__(self, size, dirty, valid, data):
        self._size = size
        self._dirty = dirty
        self._valid = valid
        self._data = data

    def __str__(self):
        return "[{}]{},{}:{}".format(self._size, self._dirty, self._valid, self._data)

    def write(self, new):
        self._data = new


class AddressSpace(enum.Enum):
    in64Bit = 0xffffffffffffffff
    in48Bit = 0xffffffffffff
    in32Bit = 0xffffffff
    in16Bit = 0xffff
