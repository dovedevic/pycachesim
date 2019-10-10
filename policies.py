from enum import Enum


class ReplacementPolicies(Enum):
    LRU = 0
    NMRU = 0
    RANDOM = 0
    LFU = 0
    NMFU = 0


class ReplacementPolicy:
    def __init__(self, policy):
        self.policy = policy
        if policy == 0:
            raise NotImplementedError("Cache replacement policy is not implemented!")

        # TODO::Implement
