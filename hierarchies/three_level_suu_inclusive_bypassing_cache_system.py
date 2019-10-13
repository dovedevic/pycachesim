from system.system import AddressSpace
from cache.cache import Cache, Block
from metrics.cache_metrics import CacheMetrics
from policies.replacement_policies import BaseReplacementPolicy as ReplacementPolicy


class ThreeLevelSUUInclusiveBypassingCacheSystem:
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

        self.stats = CacheMetrics(
            [self.IL1.name, self.DL1.name, self.UL2.name, self.UL3.name, self.MEM.name],
            [
                (self.DL1.name, self.DL1.name), (self.DL1.name, self.UL2.name), (self.DL1.name, self.UL3.name), (self.DL1.name, self.MEM.name),
                (self.UL2.name, self.UL2.name), (self.UL2.name, self.UL3.name), (self.UL2.name, self.MEM.name),
                (self.UL3.name, self.UL3.name), (self.UL3.name, self.MEM.name),
                (self.MEM.name, self.MEM.name),
                (self.MEM.name, self.UL3.name), (self.MEM.name, self.UL2.name), (self.MEM.name, self.DL1.name),
                (self.UL3.name, self.UL2.name), (self.UL3.name, self.DL1.name),
                (self.UL2.name, self.DL1.name)
            ]
        )

    def perform_fetch(self, address, for_data=True):
        cache = self.DL1 if for_data else self.IL1
        block = cache.get(address)
        hit_in = cache
        if block is None:
            self.stats.add_miss(cache.name)
            cache = self.UL2
            block = cache.get(address)
            hit_in = self.UL2

            if block is None:
                self.stats.add_miss(cache.name)
                cache = self.UL3
                block = cache.get(address)
                hit_in = self.UL3
                if block is None:
                    self.stats.add_miss(cache.name)
                    # Not in the cache, fetch from memory
                    # Allocate new block from MEM to L3
                    block = Block(address & self.UL3.get_base_address_mask(), False, self.UL3.get_policy())
                    block.read()

                    hit_in = self.MEM
                    cache = self.UL3
                    evicted = cache.put(block)
                    if evicted:
                        self.stats.add_transition(self.UL3.name, self.MEM.name, evicted.base_address())
                else:
                    block.read()
                    # Allocate new block from L3 to L2
                    block = Block(address & self.UL2.get_base_address_mask(), block.is_dirty(), self.UL2.get_policy())

                    cache = self.UL2
                    evicted = cache.put(block)
                    if evicted:
                        self.stats.add_transition(self.UL2.name, self.UL3.name, evicted.base_address())
            else:
                block.read()
                # Allocate new block from L2 to L1
                block = Block(address & (self.DL1 if for_data else self.IL1).get_base_address_mask(), block.is_dirty(), (self.DL1 if for_data else self.IL1).get_policy())

                cache = self.DL1 if for_data else self.IL1
                evicted = cache.put(block)
                if evicted:
                    self.stats.add_transition((self.DL1 if for_data else self.IL1).name, self.UL2.name, evicted.base_address())
        else:
            block.read()
        self._replacement_policy.step()
        self.stats.add_hit(hit_in.name)
        self.stats.add_transition(hit_in.name, cache.name, address)
        return cache.name, hit_in.name, block

    def perform_set(self, address, for_data=True):
        cache = self.DL1 if for_data else self.IL1
        block = cache.get(address)
        hit_in = cache
        if block is None:
            self.stats.add_miss(cache.name)
            cache = self.UL2
            block = cache.get(address)
            hit_in = self.UL2

            if block is None:
                self.stats.add_miss(cache.name)
                cache = self.UL3
                block = cache.get(address)
                hit_in = self.UL3
                if block is None:
                    self.stats.add_miss(cache.name)
                    # Not in the cache, fetch from memory
                    # Allocate new block from MEM to L3
                    block = Block(address & self.UL3.get_base_address_mask(), False, self.UL3.get_policy())
                    block.write()

                    hit_in = self.MEM
                    cache = self.UL3
                    evicted = cache.put(block)
                    if evicted:
                        self.stats.add_transition(self.UL3.name, self.MEM.name, evicted.base_address())
                else:
                    # Don't allocate new block from L2 to L1
                    block.write()
            else:
                # Don't allocate new block from L2 to L1
                block.write()
        else:
            block.write()
        self._replacement_policy.step()
        self.stats.add_hit(hit_in.name)
        self.stats.add_transition(hit_in.name, cache.name, address)
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


