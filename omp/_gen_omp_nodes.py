'''Generates nodes for parsing OMP'''

from .omp_ast_gen import OmpASTCodeGenerator

OMP_GEN = OmpASTCodeGenerator('_omp_ast.cfg')
OMP_GEN.generate(open('omp_ast.py', 'w'))
