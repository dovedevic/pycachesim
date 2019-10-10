import random


class BaseReplacementPolicy:
    def __init__(self):
        # TODO::Implement
        self._clock = 0

    @staticmethod
    def name():
        return "Default"

    @staticmethod
    def default():
        return 0

    def touch(self, block):
        return 0

    def evict(self, cache_set):
        return None

    def step(self):
        self._clock += 1


class LRUReplacementPolicy(BaseReplacementPolicy):
    @staticmethod
    def name():
        return 'LRU'

    @staticmethod
    def default():
        return 0

    def touch(self, block):
        return self._clock

    def evict(self, cache_set):
        smallest = min(cache_set, key=lambda block: block.get_policy_data())
        return smallest


class RandomReplacementPolicy(BaseReplacementPolicy):
    @staticmethod
    def name():
        return 'RAND'

    def evict(self, cache_set):
        return random.choice(cache_set)


class LFUReplacementPolicy(BaseReplacementPolicy):
    @staticmethod
    def name():
        return 'LFU'

    @staticmethod
    def default():
        return 0

    def touch(self, block):
        return block.get_policy_data() + 1

    def evict(self, cache_set):
        smallest = min(cache_set, key=lambda block: block.get_policy_data())
        return smallest


class NMFUReplacementPolicy(BaseReplacementPolicy):
    @staticmethod
    def name():
        return 'NMFU'

    @staticmethod
    def default():
        return 0

    def touch(self, block):
        return block.get_policy_data() + 1

    def evict(self, cache_set):
        mfu = max(cache_set, key=lambda block: block.get_policy_data())
        return random.choice([block for block in cache_set if block != mfu])
