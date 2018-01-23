"""Generates nodes for parsing OMP"""

from pycparser._ast_gen import ASTCodeGenerator

omp_gen = ASTCodeGenerator('_omp_ast.cfg')
omp_gen.generate(open('omp_ast.py', 'w'))

