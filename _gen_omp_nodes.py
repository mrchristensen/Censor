"""Generates nodes for parsing OMP"""

from pycparser._ast_gen import ASTCodeGenerator

OMP_GEN = ASTCodeGenerator('_omp_ast.cfg')
OMP_GEN.generate(open('omp_ast.py', 'w'))
