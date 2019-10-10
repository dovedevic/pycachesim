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
        if isinstance(other, Block):
            return True if self._base_address == other._base_address else False
        else:
            return True if self._base_address == other else False

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
