"""Bigfoot Instrumenter"""

from instrumenter.instrumenter import Instrumenter

class BigfootInstrumenter(Instrumenter): # pylint: disable=abstract-method
    """Instrumenter that registers minimal set of reads/writes"""

    # TODO set up any extra state needed for bigfoot analysis
    # in __init__ method

    def register_node_accesses(self, mode, node, append=False): # pylint: disable=too-many-branches
        """Register accesses for node"""
        # TODO override this method to register reads and writes
        # after trimming redundant ones with Bigfoot analysis
        # TODO coalesce object and array accesses
