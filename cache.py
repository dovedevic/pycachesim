
class Cache:
    def __init__(self, size, associativity, blocks, policy):
        self.size = size
        self.associativity = associativity
        self.blocks = blocks
        self.policy = policy()

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

    def put(self, block):
        """
        Put the following block into the cache. If not space is present, use the policy to evict and return the eviction
        :param block:
        :return replacement:
        """
        return None
