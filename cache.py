import math
import enum
from policies import ReplacementPolicy


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
            self._cache[cache_set] = [None for i in range(associativity)]

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

    def put(self, address, data):
        """
        Put the following address block into the cache. If not space is present, use the policy to evict and return the eviction
        :param address:
        :param data
        :return replacement:
        """

        cache_set = address << self._tag_bits >> self._tag_bits + self._offset_bits
        temp_block = Block(address >> self._offset_bits << self._offset_bits, 0, 1, data)
        if temp_block in self._cache[cache_set]:
            # Putting the same block in cache
            return None
        elif None in self._cache[cache_set]:
            placement = self._cache[cache_set].index(None)
            self._cache[cache_set][placement] = temp_block
            return None
        else:
            pass


class Block:
    def __init__(self, base_address, dirty: bool, policy: ReplacementPolicy):
        self._base_address = base_address
        self._dirty = dirty
        self._rep_policy = policy.default()

    def __str__(self):
        return "[{}]{},{}".format(hex(self._base_address), self._dirty, self._rep_policy.name())

    def __eq__(self, other):
        return True if isinstance(other, Block) and self._base_address == other._base_address else False

    def read(self):
        self._rep_policy.touch()

    def write(self):
        self._rep_policy.touch()
        self._dirty = True

    def is_dirty(self):
        return self._dirty


class AddressSpace(enum.Enum):
    in64Bit = 0xffffffffffffffff
    in48Bit = 0xffffffffffff
    in32Bit = 0xffffffff
    in16Bit = 0xffff
