
class CacheMetrics:
    def __init__(self, caches: list, transition_pairs: list):
        self._accesses = 0

        self._average_latency = 0
        self._max_latency = 999999999999
        self._min_latency = 0

        self._average_read_latency = 0
        self._average_write_latency = 0

        self._caches = dict()
        for cache in caches:
            self._caches[cache]['H'] = 0
            self._caches[cache]['M'] = 0

        self._transitions = dict()
        self._transition_pairs = transition_pairs

    def add_transition(self, t_from, t_to, address):
        if address not in self._transitions:
            self._transitions[address] = dict()
            for transition in self._transition_pairs:
                self._transitions[address]["{}->{}".format(transition[0], transition[1])] = 0
        self._transitions[address]["{}->{}".format(t_from, t_to)] += 1

    def add_hit(self, t_from):
        self._caches[t_from]['H'] += 1

    def add_miss(self, t_from):
        self._caches[t_from]['M'] += 1

    def add_latency(self, access, is_read):
        self._average_latency += access
        self._max_latency = max(self._max_latency, access)
        self._min_latency = min(self._min_latency, access)
        if is_read:
            self._average_read_latency += access
        else:
            self._average_write_latency += access

    def save(self, filename):
        with open(filename, 'w') as out:
            header = " ".join(["{}->{}".format(t[0], t[1]) for t in self._transition_pairs])
            out.write(header + "\n")
            for address in self._transitions:
                out.write("{}:{}\n".format(address, str(self._transitions[address])))
