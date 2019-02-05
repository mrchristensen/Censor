#!/usr/bin/python3
""" For checking memory access violations """

from ceskvsgcc import CESKvsGCC

class MemoryAccess(CESKvsGCC):
    """Tests basic functionality"""
    def test(self):
        """Tests basic functionality"""
        self.assert_all_memory_safe("./fixtures/faulting_memory_access", False)

if __name__ == "__main__":
    TEST = MemoryAccess()
    TEST.test()
