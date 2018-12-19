"""Scheduler class"""

import logging
from collections import deque
from cesk.interpret import execute

class Scheduler:
    """
    The Scheduler controls how execute is called
    This default implementation just keeps calling
    execute on states in the order it receives them
    back until we reach the halt state or a deadlock

    It also provides some utility functions to help
    debugging
    """

    def __init__(self, start):
        # Assumes that the runtime is set
        self.queue = deque([start])
        self.blocked = deque()

    def finished(self):
        """Return whether execution has finished"""
        return not (self.queue or self.blocked)

    def get_task(self, tid):
        """Return current state(s) for tid"""
        live = [s for s in self.queue if s.tid == tid]
        blocked = [s for s in self.blocked if s.tid == tid]
        return live + blocked

    def try_unblocking_tasks(self):
        """Try moving blocked tasks to queue"""
        states = self.blocked.copy()
        self.blocked.clear()
        self.add_states(states)

    def add_states(self, states):
        """Add states to queue and blocked"""
        for state in states:
            logging.debug("Adding %s", state)
            if state.blocking():
                self.blocked.append(state)
            else:
                state.barrier = None # prevent random blocking
                self.queue.append(state)

    def step(self):
        """Execute one step"""
        assert (self.queue or self.blocked)
        if self.queue:
            state = self.queue.popleft()
        else:
            self.try_unblocking_tasks()
            if not self.queue:
                logging.debug("DEADLOCK")
                for blocking in self.blocked:
                    logging.debug("%s", blocking)
                raise Exception("DEADLOCK")
            elif not self.queue:
                return
            state = self.queue.popleft()
        logging.info("Stepping %s", state)
        self.add_states(execute(state))
