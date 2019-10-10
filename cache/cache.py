import math
from policies import ReplacementPolicy
from cache.block import Block
from system.system import AddressSpace


class Cache:
    """
    Defines one level or type of cache, the most atomic unit in a cache system
    """

    def __init__(self, addressspace: AddressSpace, size: int, associativity: int, blocksize: int, policy: ReplacementPolicy):
        """
        The initializer for the generic single cache
        :param addressspace: The address space (of type cache.AddressSpace) this cache runs on
        :param size: The total size in bytes of the cache
        :param associativity: The number of ways in a set
        :param blocksize: The size in bytes of a single block
        :param policy: The replacement policy (of type policies.ReplacementPolicy) this cache runs evictions on
        """
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

    def get(self, address):
        """
        Access the cache and attempt to get a block from an address
        :param address: The address to be fetched
        :return hit: None if miss, Block if hit
        """
        cache_set = ((2 ** self._tag_bits) << (self._offset_bits + self._index_bits)) & address >> self._offset_bits
        base_address = address >> self._offset_bits << self._offset_bits
        if base_address in self._cache[cache_set]:
            fetched = self._cache[cache_set].index(base_address)
            return self._cache[cache_set][fetched]
        else:
            return None

    def put(self, block: Block):
        """
        Put the following block into the cache. If not space is present, use the policy to evict and return the
        eviction. If space is available or the block is present, place and return
        :param block:
        :return replacement:
        """
        cache_set = ((2 ** self._tag_bits) << (self._offset_bits + self._index_bits)) & block.base_address() >> self._offset_bits
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
