
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



