#!/usr/bin/python3
"""Unittest Driver"""
import sys
import unittest

sys.path[0:0] = ['.', '..']

SUITE = unittest.TestLoader().loadTestsFromNames(
    [   #'test_memory.yaml_tester'])
        'test_transforms.test_node_transformer',
        'test_transforms.test_for_to_while',
        'test_transforms.test_if_goto',
        'test_transforms.test_switch_to_if',
        'test_transforms.test_omp_for',
        'test_transforms.test_omp_critical',
        'test_transforms.test_do_while_to_goto',
        'test_transforms.test_while_to_do_while',
        'test_transforms.test_omp_parallel',
        'test_transforms.test_omp_barrier',
        'test_transforms.test_omp_master',
        'test_transforms.test_omp_single',
        'test_transforms.test_omp_task',
        'test_transforms.test_omp_flush',
        'test_transforms.test_omp_parallel_for',
        'test_transforms.test_omp_sections',
        'test_transforms.test_omp_section',
        'test_transforms.test_omp_parallel_sections',
        'test_transforms.test_omp_atomic',
        'test_transforms.test_omp_taskloop',
        'test_transforms.test_omp_taskwait',
        'test_transforms.test_omp_taskgroup',
        'test_transforms.test_omp_cancel',
        'test_transforms.test_omp_cancellation_point',
        'test_transforms.test_omp_threadprivate',
        'test_transforms.test_omp_simd',
        'test_transforms.test_alpha_name',
        'test_transforms.test_id_generator',
        'test_transforms.test_remove_compound_assignment',
        'test_transforms.test_insert_explicit_type_casts',
        'test_transforms.test_single_return',
        'test_transforms.test_remove_multidimensional_array',
        'test_transforms.test_lift_to_compound_block',
        'test_transforms.test_sequence',
        'test_transforms.test_break_to_goto',
        'test_transforms.test_remove_init_lists',
        'test_transforms.test_simplify_omp_for',
        'test_transforms.test_omp_not_implemented',
        'test_transforms.test_sizeof_type',
        'test_transforms.test_change_void_pointer',
        'test_transforms.test_struct_ref_to_pointer',
        'test_transforms.test_unary_op',
        'test_transforms.test_remove_typedef',
        'test_instrumenter.test_logger',
        'test_instrumenter.test_instrumenter',
        'test_ssl.test_correct_call_order'
    ]) #"""
TESTRESULT = unittest.TextTestRunner(verbosity=2).run(SUITE)
sys.exit(0 if TESTRESULT.wasSuccessful() else 1)
