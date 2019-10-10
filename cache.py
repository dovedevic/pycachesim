import math
import enum
from policies import ReplacementPolicy


class Block:
    """
    Defines the most atomic unit in a cache, the block
    """

    def __init__(self, base_address, dirty: bool, policy: ReplacementPolicy):
        """
        Initializer for the generic cache block
        :param base_address: The tag and index of an address
        :param dirty: The determination if this block was ever writen to or not
        :param policy_data: The replacement policy metadata that keeps track of the block
        """
        self._base_address = base_address
        self._dirty = dirty
        self._policy = policy
        self._policy_data = policy.default()

    def __str__(self):
        return "[{}]{},{}:{}".format(hex(self._base_address), self._dirty, self._policy.name(), self._policy_data)

    def __eq__(self, other):
        return True if isinstance(other, Block) and self._base_address == other._base_address else False

    def read(self):
        """
        Perform a simulated read on this cache block
        :return: nothing
        """
        self._policy_data = self._policy.touch(self)

    def write(self):
        """
        Perform a simulated write on this cache block
        :return: nothing
        """
        self._policy_data = self._policy.touch(self)
        self._dirty = True

    def is_dirty(self):
        """
        Returns if this block is written to, or dirty
        :return: boolean, if this block is dirty
        """
        return self._dirty

    def base_address(self):
        """
        Returns this blocks base address
        :return: int, the base address
        """
        return self._base_address


class Cache:
    def __init__(self, addressspace, size, associativity, blocksize, policy: ReplacementPolicy):
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

    def put(self, block: Block):
        """
        Put the following block into the cache. If not space is present, use the policy to evict and return the
        eviction. If space is available or the block is present, place and return
        :param block:
        :return replacement:
        """

        cache_set = block.base_address() << self._tag_bits >> self._tag_bits + self._offset_bits
        if block in self._cache[cache_set]:
            # Block is existing in cache, assuming rewrite
            replacement = self._cache[cache_set].index(block)
            self._cache[cache_set][replacement] = block
            return None
        elif None in self._cache[cache_set]:
            # Space available in cache for new block, place it
            placement = self._cache[cache_set].index(None)
            self._cache[cache_set][placement] = block
            return None
        else:
            # Block is not existing in cache and space is not available, evict
            evicted_block_index = self._policy.evict(self._cache[cache_set])
            evicted_block = self._cache[cache_set][evicted_block_index]
            self._cache[cache_set][evicted_block_index] = block
            return evicted_block


class AddressSpace(enum.Enum):
    """
    Defines the address space supported by a system or cache
    """
    in128Bit = 0xffffffffffffffffffffffffffffffff
    in112Bit = 0xffffffffffffffffffffffffffff
    in96Bit = 0xffffffffffffffffffffffff
    in80Bit = 0xffffffffffffffffffff
    in64Bit = 0xffffffffffffffff
    in48Bit = 0xffffffffffff
    in32Bit = 0xffffffff
    in16Bit = 0xffff
    in8Bit = 0xff
