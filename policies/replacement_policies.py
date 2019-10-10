import random


class BaseReplacementPolicy:
    """
    Defines the base set of features a replacement policy controls. These include its clock counter, its name, its
    default or instantiation number, its eviction properties, and its update / touch property
    """
    def __init__(self):
        """
        Assuming the policy is instantiated at startup and is not changing throughout execution
        """
        self._clock = 0

    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return "Default"

    def default(self):
        """
        The default value for a new block
        :return: The current clock cycle
        """
        return self._clock

    def touch(self, block):
        """
        Update the block's replacement policy metadata
        :param block: The block to update
        :return: The new data that should be stored in the blocks metadata section
        """
        return block.get_policy_data()

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        return None

    def step(self):
        """
        Update the step counter for all replacement policies
        :return: None
        """
        self._clock += 1


class LRUReplacementPolicy(BaseReplacementPolicy):
    """
    This defines the most commonly used eviction policy, LRU or Least Recently Used. This policy evicts the block in the
    set that was the last one to be touched, read, or updated. It is the oldest hit in the set
    """
    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return 'LRU'

    def touch(self, block):
        """
        Update the block's replacement policy metadata
        :param block: The block to update
        :return: The new data that should be stored in the blocks metadata section
        """
        return self._clock

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        smallest = min(cache_set, key=lambda block: block.get_policy_data())
        return smallest


class RandomReplacementPolicy(BaseReplacementPolicy):
    """
    This defines the RAND or Random replacement policy. This policy evicts a random block in the set
    """
    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return 'RAND'

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        return random.choice(cache_set)


class LFUReplacementPolicy(BaseReplacementPolicy):
    """
    This defines the LFU or Least Frequently Used replacement policy. This policy evicts the block in the set that has
    been accessed the least amount of times among all other blocks, regardless of insertion time.
    """
    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return 'LFU'

    def default(self):
        """
        The default value for a new block in LFU is zero
        :return: The current clock cycle
        """
        return 0

    def touch(self, block):
        """
        Update the block's replacement policy metadata
        :param block: The block to update
        :return: The new data that should be stored in the blocks metadata section
        """
        return block.get_policy_data() + 1

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        smallest = min(cache_set, key=lambda block: block.get_policy_data())
        return smallest


class NMFUReplacementPolicy(BaseReplacementPolicy):
    """
    This defines the NMFU or Not Most Frequently Used replacement policy. This policy evicts a random block from the set
    with the condition that it is not the most frequently used among the set
    """
    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return 'NMFU'

    def default(self):
        """
        The default value for a new block in MFU is zero
        :return: The current clock cycle
        """
        return 0

    def touch(self, block):
        """
        Update the block's replacement policy metadata
        :param block: The block to update
        :return: The new data that should be stored in the blocks metadata section
        """
        return block.get_policy_data() + 1

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        mfu = max(cache_set, key=lambda block: block.get_policy_data())
        return random.choice([block for block in cache_set if block != mfu])


class NMRUReplacementPolicy(BaseReplacementPolicy):
    """
    This defines the NMRU or Not Most Recently Used replacement policy. This policy evicts a random block from the set
    with the condition that it is not the most recently used among the set
    """
    @staticmethod
    def name():
        """
        The name of this policy
        :return: str
        """
        return 'NMRU'

    def touch(self, block):
        """
        Update the block's replacement policy metadata
        :param block: The block to update
        :return: The new data that should be stored in the blocks metadata section
        """
        return self._clock

    def evict(self, cache_set):
        """
        Evict a block from the given set by the property defined in this policy
        :param cache_set: The set on which to evict a block
        :return: the evicted block, assuming there is something to evicts
        """
        mru = max(cache_set, key=lambda block: block.get_policy_data())
        return random.choice([block for block in cache_set if block != mru])
