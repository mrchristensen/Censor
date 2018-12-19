"""OpenMP Runtime"""

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=too-many-instance-attributes
# pylint: disable=no-self-use
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=invalid-name
# pylint: disable=unused-argument

import logging
from copy import deepcopy
from omp.omp_ast import *
from pycparser.c_ast import ID, Constant
import cesk.interpret as interpreter
from cesk.structures import State, Kont, Ctrl
import cesk.linksearch as ls

CRITICAL_SECTION = "CRITICAL_SECTION"

def getenv(env, var, default):
    """Get environment variable from default"""
    if env.get(var) is None:
        return default
    return env.get(var)

class ReleaseKont(Kont):
    """Decrease barrier count and either die or return state"""

    def __init__(self, parent_state, address, die, stall):
        super().__init__(parent_state, address)
        self.die = die
        self.stall = stall

    def invoke(self, state, value=None):
        """Update barrier and return new state"""
        # address is interpreted as the barrier
        state.get_runtime().remove_from_barrier(self.address)
        if self.die:
            logging.debug("Dying after setting barrier to %d",
                          state.get_runtime().get_barrier(self.address))
            return None
        # point state to correct barrier
        next_state = State(self.ctrl, self.envr, state.stor,
                           self.kont_addr, state.tid, state.master,
                           self.address)
        if not self.stall:
            next_state = next_state.get_next()
        logging.debug("Decremented barrier to %d, returning %s",
                      state.get_runtime().get_barrier(self.address),
                      next_state)
        return next_state

def encountering_thread_kont(state, address):
    """Return a ReleaseKont for encountering threads"""
    return ReleaseKont(state, address, False, True)

def worker_thread_kont(state, address):
    """Return a ReleaseKont for a worker"""
    return ReleaseKont(state, address, True, True)

def critical_section_kont(state, address):
    """Return a ReleaseKont for exiting a critical section"""
    return ReleaseKont(state, address, False, False)

class AcquireKont(Kont):
    """Increase barrier count and execute current ctrl"""

    def invoke(self, state, value=None):
        """Update barrier and return new state"""
        # assumes ctrl is a critical section
        block = self.ctrl.stmt().block
        kont_type = critical_section_kont
        parent = State(self.ctrl, self.envr, state.stor,
                       self.kont_addr, state.tid, state.master,
                       state.barrier)
        next_state = state.get_runtime().get_structured_block(
            parent, block, kont_type, state.tid,
            self.address)
        logging.debug("Incremented barrier to %d, returning %s",
                      state.get_runtime().get_barrier(self.address),
                      next_state)
        return next_state

class OmpRuntime():
    """OpenMP Runtime"""

    tid_counter = 0

    @staticmethod
    def allocT(state):
        """Return task id"""
        OmpRuntime.tid_counter += 1
        return OmpRuntime.tid_counter

    def __init__(self, env):
        self.num_threads = [int(getenv(env, 'OMP_NUM_THREADS', 2))]
        self.thread_limit = int(getenv(env, 'OMP_THREAD_LIMIT', 2))
        self.dynamic = bool(getenv(env, 'OMP_DYNAMIC', True))
        self.levels = 0
        self.active_levels = 0
        self.max_active_levels = int(getenv(env, 'OMP_MAX_ACTIVE_LEVELS', 1))
        schedule_kind = getenv(env, 'OMP_SCHEDULE', 'dynamic')
        self.schedule = (schedule_kind, 1)
        self.nested = bool(getenv(env, 'OMP_NESTED', False))
        self.contention_group = 1
        self.barriers = {CRITICAL_SECTION:0}

    def get_num_child_threads(self):
        """
        Return the number of implicit tasks (threads) to generate
        for a parallel region not including the encountering thread
        """
        threads_busy = self.contention_group
        threads_requested = self.num_threads[0]
        threads_available = self.thread_limit - threads_busy + 1
        if self.active_levels >= 1 and not self.nested:
            num_threads = 0
        elif self.active_levels == self.max_active_levels:
            num_threads = 0
        elif self.dynamic and threads_requested <= threads_available:
            num_threads = threads_requested - 1
        elif self.dynamic and threads_requested > threads_available:
            num_threads = threads_available - 1
        elif not self.dynamic and threads_requested <= threads_available:
            num_threads = threads_requested - 1
        else:
            num_threads = 0
        self.contention_group += num_threads
        return num_threads

    def get_loop_iterations(self, state):
        """Return iteration values for thread encountering OmpFor"""
        iterations = []
        omp_for = state.ctrl.stmt()
        nth_thread = state.tid - state.master
        # just create all tasks with master thread for now
        # eventually the schedule type will need to be considered
        # in order to make barrier counter accurate without assuming
        # anything about the schedule, every thread needs to create at
        # least one task. Otherwise, if the first thread to encounter
        # the loop doesn't create any tasks, it's barrier counter will
        # be 0 and it will move past the barrier illegaly
        if nth_thread != 0:
            return iterations
        # relies on simplify_omp_for, lift_to_compound and unary_op transforms
        iter_var = omp_for.loops.init.lvalue.name
        init = interpreter.get_value(omp_for.loops.init.rvalue, state)
        cond = omp_for.loops.cond
        bound = interpreter.get_value(cond.right, state)
        binop = omp_for.loops.next.rvalue
        next_op = binop.op
        if isinstance(binop.left, ID) and binop.left.name == iter_var:
            lhs = True
            next_expr = interpreter.get_value(binop.right, state)
        else:
            lhs = False
            next_expr = interpreter.get_value(binop.left, state)
        current = interpreter.get_value(
            Constant(init.type_of, str(init.get_value())), state)
        while current\
                .perform_operation(cond.op, bound)\
                .get_truth_value():
            iterations.append((iter_var, current))
            if lhs:
                current = current.perform_operation(next_op, next_expr)
            else:
                current = next_expr.perform_operation(next_op, current)
        return iterations

    def get_structured_block(self, state, block, kont_type, tid, barrier,
                             private=None):
        """Return task for structured block"""
        self.add_to_barrier(barrier)
        ctrl = Ctrl(0, block)
        if isinstance(private, list):
            envr = deepcopy(state.envr)
            envr.scope_id = envr.allocF(state)
        else:
            envr = state.envr
        kont = kont_type(state, barrier)
        kont_addr = Kont.allocK(state, ctrl, envr)
        state.stor.write_kont(kont_addr, kont)
        master = state.master if tid == state.tid else state.master
        new_state = State(ctrl, envr, state.stor, kont_addr, tid,
                          master, None) # don't block yet
        if isinstance(private, list):
            for var, val in private:
                decl = ls.LinkSearch.decl_lut[var]
                new_state = interpreter.decl_helper(decl, new_state)
                new_address = new_state.envr.get_address(decl.name)
                new_state.stor.write(new_address, val)
        return new_state

    def get_thread_team(self, state):
        """Return states for descendant threads of parallel region"""
        omp_parallel = state.ctrl.stmt()
        block = omp_parallel.block
        master = self.get_structured_block(
            state, block, encountering_thread_kont, state.tid, omp_parallel)
        threads = [master]
        for _ in range(self.get_num_child_threads()):
            tid = OmpRuntime.allocT(state)
            threads.append(self.get_structured_block(
                state, block, worker_thread_kont, tid, omp_parallel))
        return threads

    def get_loop_tasks(self, state):
        """Return tasks to execute loop body"""
        omp_for = state.ctrl.stmt()
        block = omp_for.loops.stmt
        # todo don't place barrier if nowait clause is present
        thread = State(state.ctrl, state.envr, state.stor, state.kont_addr,
                       state.tid, state.master, omp_for)
        states = [thread]
        for iter_var in self.get_loop_iterations(state):
            tid = OmpRuntime.allocT(state)
            states.append(
                self.get_structured_block(state, block, worker_thread_kont,
                                          tid, omp_for, [iter_var]))
        return states

    def get_barrier(self, barrier):
        """Get barrier counter"""
        if barrier is None or barrier not in self.barriers:
            return -1
        return self.barriers[barrier]

    def get_critical_section(self, state):
        """Return state for executing critical section body"""
        critical = state.ctrl.stmt()
        block = critical.block
        if self.barrier_clear(CRITICAL_SECTION):
            return self.get_structured_block(
                state, block, critical_section_kont,
                state.tid, CRITICAL_SECTION)
        ctrl = Ctrl(critical)
        kont = AcquireKont(state, CRITICAL_SECTION)
        kont_addr = Kont.allocK(state, ctrl, state.envr)
        state.stor.write_kont(kont_addr, kont)
        next_state = State(ctrl, state.envr, state.stor, kont_addr, state.tid,
                           state.master, CRITICAL_SECTION)
        return next_state

    def barrier_clear(self, barrier):
        """Return whether barrier is clear"""
        val = self.get_barrier(barrier)
        return val in (-1, 0)

    def add_to_barrier(self, barrier):
        """Add another task to barrier"""
        if barrier is None:
            return
        if self.get_barrier(barrier) == -1:
            self.barriers[barrier] = 0
        self.barriers[barrier] += 1

    def remove_from_barrier(self, barrier):
        """Mark task as reaching barrier"""
        if self.barrier_clear(barrier):
            return
        self.barriers[barrier] -= 1
