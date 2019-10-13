
class CacheMetrics:
    """
    CacheMetrics tracks transitions, latencies and hits / misses for an entire cache system
    """

    def __init__(self, caches: list, transition_pairs: list):
        """
        Initializer for the CacheMetrics class. Sets up metrics, initializes storage metadata, and handles logging
        :param caches: A list of cache.names
        :param transition_pairs: A list of tuples (cache.name, cache.name) representing all possible transition states
        from the cache list and any possible transition between them (from, to).
        """
        self._accesses = 0

        self._average_latency = 0
        self._max_latency = 999999999999
        self._min_latency = 0

        self._average_read_latency = 0
        self._average_write_latency = 0

        self._caches = dict()
        for cache in caches:
            self._caches[cache] = dict()
            self._caches[cache]['H'] = 0
            self._caches[cache]['M'] = 0

        self._transitions = dict()
        self._transition_pairs = transition_pairs
        self._address_tracker = dict()

    def add_transition(self, t_from, t_to, address):
        """
        Add a transition from one cache to another for a block / address
        :param t_from: The cache name where the block originated
        :param t_to: The cache name where the block is destined
        :param address: The address/block that is being moved
        :return:
        """
        if address not in self._transitions:
            self._transitions[address] = dict()
            for transition in self._transition_pairs:
                self._transitions[address]["{}->{}".format(transition[0], transition[1])] = 0
        self._transitions[address]["{}->{}".format(t_from, t_to)] += 1

    def add_hit(self, hit_in):
        """
        Log a hit from the given cache
        :param hit_in: The Cache name where the hit occurred
        :return: None
        """
        self._caches[hit_in]['H'] += 1

    def add_miss(self, miss_from):
        """
        Log a miss from the given cache
        :param miss_from: The Cache name where the miss occurred
        :return: None
        """
        self._caches[miss_from]['M'] += 1

    def add_latency(self, access, is_read):
        """
        Add latency time with the given access time. Also specify if the latency was for a read or write
        :param access: The time in pre-described units in the cache definition
        :param is_read: Whether the access time was used for a read or write
        :return: None
        """
        self._average_latency += access
        self._max_latency = max(self._max_latency, access)
        self._min_latency = min(self._min_latency, access)
        if is_read:
            self._average_read_latency += access
        else:
            self._average_write_latency += access

    def save(self, filename):
        """
        Save the metrics for the run. Saves the overall stats, latencies, and transitions
        :param filename: The file or directory to where the output will be saved
        :return: None
        """
        with open(filename, 'w') as out:
            out.write("Overall Stats:\n")
            for cache in self._caches:
                out.write("{} - {} misses {} hits\n".format(cache, self._caches[cache]["M"], self._caches[cache]["H"]))
            out.write("Transition Stats:\n")
            header = " ".join(["{}->{}".format(t[0], t[1]) for t in self._transition_pairs])
            out.write(header + "\n")
            for address in self._transitions:
                out.write("{}:{}\n".format(hex(address), str(self._transitions[address])))
