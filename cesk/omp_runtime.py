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
from pycparser.c_ast import ID, Constant, Compound
import cesk.interpret as interpreter
from cesk.structures import State, Kont, Ctrl
import cesk.linksearch as ls

CRITICAL_SECTION = "CRITICAL_SECTION"

def getenv(env, var, default):
    """Get environment variable from default"""
    if env.get(var) is None:
        return default
    return env.get(var)

class ContinueKont(Kont):
    """Continue after barrier"""

    def invoke(self, state, value=None):
        """Update barrier and return new state"""
        # address is interpreted as the barrier
        state.get_runtime().remove_from_barrier(self.address)
        # point state to correct barrier
        next_state = State(self.ctrl, self.envr, state.stor,
                           self.kont_addr, state.tid, state.master,
                           self.address)
        logging.debug("ContinueKont returning %s", next_state)
        return next_state

class DieKont(Kont):
    """Die at barrier"""

    def invoke(self, state, value=None):
        """Update barrier and die"""
        # address is interpreted as the barrier
        state.get_runtime().remove_from_barrier(self.address)
        logging.debug("DieKont setting barrier to %d",
                      state.get_runtime().get_barrier(self.address))
        # return None to die

class CriticalKont(Kont):
    """Continuation for thread after executing critical section"""

    def invoke(self, state, value=None):
        """Update barrier and return new state"""
        # address is interpreted as the barrier
        state.get_runtime().release_critical_section()
        new_state = State(self.ctrl, self.envr, state.stor,
                          self.kont_addr, state.tid, state.master,
                          None)
        return new_state.get_next()

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
                             private=None, inherit_envr=True):
        """Return task for structured block"""
        self.add_to_barrier(barrier)
        if isinstance(block, Compound):
            ctrl = Ctrl(0, block)
        else:
            ctrl = Ctrl(block)
        if inherit_envr:
            envr = deepcopy(state.envr)
            envr.scope_id = envr.allocF(state)
        else:
            envr = state.envr
        if kont_type is not None:
            kont = kont_type(state, barrier)
            kont_addr = Kont.allocK(state, ctrl, envr)
            state.stor.write_kont(kont_addr, kont)
        else:
            kont_addr = state.kont_addr
        if tid != state.tid:
            master = state.tid
        else:
            master = state.master
        new_state = State(ctrl, envr, state.stor, kont_addr, tid,
                          master, None) # don't block yet
        if isinstance(private, list) and inherit_envr:
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
        kont_type = ContinueKont
        master = self.get_structured_block(state, block, kont_type, state.tid,
                                           omp_parallel)
        threads = [master]
        kont_type = DieKont
        for _ in range(self.get_num_child_threads()):
            tid = OmpRuntime.allocT(state)
            threads.append(self.get_structured_block(
                state, block, kont_type, tid, omp_parallel))
        return threads

    def get_loop_tasks(self, state):
        """Return tasks to execute loop body"""
        omp_for = state.ctrl.stmt()
        block = omp_for.loops.stmt
        kont_type = ContinueKont
        # todo don't place barrier if nowait clause is present
        thread = self.get_structured_block(state, omp_for, kont_type,
                                           state.tid, omp_for, None, False)
        states = [*thread.get_next()]
        kont_type = DieKont
        for iter_var in self.get_loop_iterations(state):
            tid = OmpRuntime.allocT(state)
            states.append(
                self.get_structured_block(state, block, kont_type,
                                          tid, omp_for, [iter_var]))
        return states

    def get_barrier(self, barrier):
        """Get barrier counter"""
        if barrier is None or barrier not in self.barriers:
            return -1
        return self.barriers[barrier]

    def get_critical_section(self, state):
        """Return state for executing critical section body"""
        if self.critical_section_locked():
            return State(state.ctrl, state.envr, state.stor, state.kont_addr,
                         state.tid, state.master, CRITICAL_SECTION)
        else:
            self.lock_critical_section()
            block = state.ctrl.stmt()
            return self.get_structured_block(state, block, CriticalKont,
                                             state.tid, None, None, False)

    def barrier_clear(self, barrier):
        """Return whether barrier is clear"""
        return barrier is None or barrier not in self.barriers\
                or self.barriers[barrier] == 0

    def add_to_barrier(self, barrier):
        """Add another task to barrier"""
        if barrier is None:
            return
        if barrier not in self.barriers:
            self.barriers[barrier] = 0
        self.barriers[barrier] += 1

    def remove_from_barrier(self, barrier):
        """Mark task as reaching barrier"""
        if self.barrier_clear(barrier):
            return
        self.barriers[barrier] -= 1

    def critical_section_locked(self):
        """Return whether another thread is occupying a critical section"""
        return self.barrier_clear(CRITICAL_SECTION)

    def lock_critical_section(self):
        """Lock critical section"""
        self.add_to_barrier(CRITICAL_SECTION)

    def release_critical_section(self):
        """Release critical section"""
        self.remove_from_barrier(CRITICAL_SECTION)
