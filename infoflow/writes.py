"""Delta, or the writes map. This class is used during abstract interpretation
    for recording reads and writes. The other data structures necessary for
    information flow tracking are contained in the enclosing infoflow module."""

class WritesMap:
    """A class that tracks writes to memory during abstract interpretation."""

    def __init__(self):
        self.writes = {}

    def record(self, loc, dest, sources):
        """Record a write event that occurred at loc to dest. sources is a set
            containing all of the addresses affecting the write's value."""
        if loc in self.writes:
            local = self.writes[loc]
            if dest in local:
                local[dest] = local[dest] | sources
            else:
                local[dest] = sources
        else:
            self.writes[loc] = {dest : sources}

    def written_at(self, loc):
        """Retrieve the set of addresses written at a given location."""
        if loc in self.writes:
            return self.writes[loc].keys()
        else:
            return frozenset()

    def sources(self, loc, dest):
        """Retrieve the set of addresses influencing a write at a location and
            to a destination address."""
        if loc in self.writes and dest in self.writes[loc]:
            return self.writes[loc][dest]
        else:
            return frozenset()
