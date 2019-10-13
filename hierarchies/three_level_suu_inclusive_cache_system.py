from system.system import AddressSpace
from cache.cache import Cache, Block
from policies.replacement_policies import BaseReplacementPolicy as ReplacementPolicy


class ThreeLevelSUUInclusiveCacheSystem:
    def __init__(self, space: AddressSpace, policy: ReplacementPolicy, level_sizes: list, level_associativites: list, blocksize):
        self._space = space
        self._replacement_policy = policy
        self._blocksize = blocksize

        if not isinstance(level_sizes, list) or len(level_sizes) != 3:
            raise AttributeError("Field 'level_sizes' must be a list of length 3 indicating I/DL1, UL2, and UL3 cache sizes")

        if not isinstance(level_associativites, list) or len(level_associativites) != 3:
            raise AttributeError("Field 'level_associativites' must be a list of length 3 indicating I/DL1, UL2, and UL3 associativity")

        self.DL1 = Cache(space, level_sizes[0], level_associativites[0], blocksize, policy, name='DL1')
        self.IL1 = Cache(space, level_sizes[0], level_associativites[0], blocksize, policy, name='IL1')
        self.UL2 = Cache(space, level_sizes[1], level_associativites[1], blocksize, policy, name='UL2')
        self.UL3 = Cache(space, level_sizes[2], level_associativites[2], blocksize, policy, name='UL3')
        self.MEM = Cache(space, blocksize, 1, blocksize, policy, name='MEM')

    def perform_fetch(self, address, for_data=True):
        cache = self.DL1 if for_data else self.IL1
        block = cache.get(address)
        hit_in = cache
        if not block:
            cache = self.UL2
            block = cache.get(address)
            hit_in = self.UL2

            if not block:
                cache = self.UL3
                block = cache.get(address)
                hit_in = self.UL3
                if not block:
                    # Not in the cache, fetch from memory
                    # Allocate new block from MEM to L3
                    block = Block(address & self.UL3.get_base_address_mask(), False, self.UL3.get_policy())
                    block.read()
                    # Don't care about evictions due to inclusivity
                    hit_in = self.MEM
                    cache = self.UL3
                    cache.put(block)
                else:
                    block.read()

                # Allocate new block from L3 to L2
                block = Block(address & self.UL2.get_base_address_mask(), block.is_dirty(), self.UL2.get_policy())
                block.read()
                # Don't care about evictions due to inclusivity
                cache = self.UL2
                cache.put(block)
            else:
                block.read()

            # Allocate new block from L2 to L1
            block = Block(address & (self.DL1 if for_data else self.IL1).get_base_address_mask(), block.is_dirty(), (self.DL1 if for_data else self.IL1).get_policy())
            block.read()
            # Don't care about evictions due to inclusivity
            cache = self.DL1 if for_data else self.IL1
            cache.put(block)
        else:
            block.read()
        self._replacement_policy.step()
        return cache.name, hit_in.name, block

    def perform_set(self, address, for_data=True):
        cache = self.DL1 if for_data else self.IL1
        block = cache.get(address)
        hit_in = cache
        if not block:
            cache = self.UL2
            block = cache.get(address)
            hit_in = self.UL2

            if not block:
                cache = self.UL3
                block = cache.get(address)
                hit_in = self.UL3
                if not block:
                    # Not in the cache, fetch from memory
                    # Allocate new block from MEM to L3
                    block = Block(address & self.UL3.get_base_address_mask(), False, self.UL3.get_policy())
                    block.write()
                    # Don't care about evictions due to inclusivity
                    hit_in = self.MEM
                    cache = self.UL3
                    cache.put(block)
                else:
                    block.write()

                # Allocate new block from L3 to L2
                block = Block(address & self.UL2.get_base_address_mask(), block.is_dirty(), self.UL2.get_policy())
                block.write()
                # Don't care about evictions due to inclusivity
                cache = self.UL2
                cache.put(block)
            else:
                block.write()

            # Allocate new block from L2 to L1
            block = Block(address & (self.DL1 if for_data else self.IL1).get_base_address_mask(), block.is_dirty(), (self.DL1 if for_data else self.IL1).get_policy())
            block.write()
            # Don't care about evictions due to inclusivity
            cache = self.DL1 if for_data else self.IL1
            cache.put(block)
        else:
            block.write()
        self._replacement_policy.step()
        return cache.name, hit_in.name, block

    def populate(self, address, cache: Cache, dirty=False):
        base_address = address & cache.get_base_address_mask()
        block = Block(base_address, dirty, self._replacement_policy)
        error = cache.put(block)
        if error is not None:
            raise EnvironmentError(
                """Cold placement of the following address caused an eviction in the cache. You probably didn't want this.

                Address: {} was placed into the {} cache. 
                Address: {} was evicted as a result!
                """.format(hex(base_address), cache.name, error.base_address)
            )


