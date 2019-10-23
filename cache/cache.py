import math
from policies.replacement_policies import BaseReplacementPolicy as ReplacementPolicy
from cache.block import Block
from system.system import AddressSpace


class Cache:
    """
    Defines one level or type of cache, the most atomic unit in a cache system
    """

    def __init__(self, addressspace: AddressSpace, size: int, associativity: int, blocksize: int, policy: ReplacementPolicy, name="Cache", rlatency=0, wlatency=0):
        """
        The initializer for the generic single cache
        :param addressspace: The address space (of type cache.AddressSpace) this cache runs on
        :param size: The total size in bytes of the cache
        :param associativity: The number of ways in a set
        :param blocksize: The size in bytes of a single block
        :param policy: The replacement policy (of type policies.ReplacementPolicy) this cache runs evictions on
        :param name: The custom name of this cache object
        :param rlatency: The latency in some uniform time unit that this cache requires for a read
        :param wlatency: The latency in some uniform time unit that this cache requires for a write
        """
        self._addressspace = addressspace.value
        self._size = size
        self._associativity = associativity
        self._blocksize = blocksize
        self._blocks = size // blocksize
        self._sets = self._blocks // associativity
        self.name = name
        self.read_latency = rlatency
        self.write_latency = wlatency

        self._offset_bits = int(math.log(self._blocksize, 2))
        self._index_bits = int(math.log(self._sets, 2))
        self._tag_bits = int(math.log(addressspace.value + 1, 2)) - self._offset_bits - self._index_bits

        self._base_address_mask = (2 ** (self._index_bits + self._tag_bits) - 1) << self._offset_bits

        self._policy = policy

        self._cache = dict()
        for cache_set in range(0, self._sets):
            self._cache[cache_set] = [None for _ in range(associativity)]

    def get(self, address):
        """
        Access the cache and attempt to get a block from an address
        :param address: The address to be fetched
        :return hit: None if miss, Block if hit
        """
        cache_set = (self._sets - 1) & (address >> self._offset_bits)
        base_address = address >> self._offset_bits << self._offset_bits
        if base_address in self._cache[cache_set]:
            fetched = self._cache[cache_set].index(base_address)
            return self._cache[cache_set][fetched]
        else:
            return None

    def remove(self, block: Block):
        """
        Remove the block from the cache, if it is present
        :param block: The block to be removed
        :return: None
        """
        cache_set = (self._sets - 1) & (block.base_address() >> self._offset_bits)
        if block in self._cache[cache_set]:
            # Block is present in set, remove it
            placement = self._cache[cache_set].index(block)
            self._cache[cache_set][placement] = None

    def remove_base(self, base_address):
        """
        Remove the block that corresponds to base_address from the cache, if it is present
        :param base_address: The base_address of the block to be removed
        :return: None
        """
        cache_set = (self._sets - 1) & (base_address >> self._offset_bits)
        if base_address in self._cache[cache_set]:
            # Block is present in set, remove it
            placement = self._cache[cache_set].index(base_address)
            self._cache[cache_set][placement] = None
        else:
            print('shouldnt happen')

    def put(self, block: Block):
        """
        Put the following block into the cache. If not space is present, use the policy to evict and return the
        eviction. If space is available or the block is present, place and return
        :param block: The block to be placed
        :return replacement:
        """
        cache_set = (self._sets - 1) & (block.base_address() >> self._offset_bits)
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
            evicted_block = self._policy.evict(self._cache[cache_set])
            evicted_block_index = self._cache[cache_set].index(evicted_block)
            self._cache[cache_set][evicted_block_index] = block
            return evicted_block

    def get_base_address_mask(self):
        """
        Return the base address mask
        :return: base address mask
        """
        return self._base_address_mask

    def get_policy(self):
        """
        Return the replacement policy for this cache
        :return: replacement policy
        """
        return self._policy

    def get_block_size(self):
        """
        Return the size of the blocks in this cache
        :return: block size
        """
        return self._blocksize
