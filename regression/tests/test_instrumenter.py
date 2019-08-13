
'''Run regression tests on dataracebench tests.'''

import tempfile
from os.path import join
import utils
from regression.tests.helpers import RegressionTestCase, \
        get_fixtures, \
        _parse_ast_from_file, \
        _temp_copy, \
        _compile_c
from transforms import transform
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from transforms.id_generator import IDGenerator
from instrumenter.instrumenter import Instrumenter

class TestDataRaceBench(RegressionTestCase):
    '''Test dataracebench micro-benchmarks'''

    def setUp(self): #pylint: disable=invalid-name
        '''Setup'''
        self.fixtures = '../dataracebench/micro-benchmarks/no'
        self.includes = ['../dataracebench/micro-benchmarks',
                         '../dataracebench/micro-benchmarks/utilities']
        self.add_flags = [
            '-lm',
            '-fopenmp',
            '../dataracebench/micro-benchmarks/utilities/polybench.c',
            '-DPOLYBENCH_NO_FLUSH_CACHE',
            '-DPOLYBENCH_TIME',
            '-D_POSIX_C_SOURCE=200112L'
        ]
        self.instrumenter = None

    def instrument(self, ast):
        '''Instrument AST'''
        ast = transform(ast)
        id_generator = IDGenerator(ast)
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.instrumenter = Instrumenter(id_generator, environments)
        return self.instrumenter.visit(ast)

    def run_compilation(self, fixture):
        '''Run compilation and return result'''
        benchmark = _temp_copy(fixture)
        utils.preserve_include_preprocess(benchmark.name)
        ast = _parse_ast_from_file(benchmark.name, self.includes)
        ast = self.instrument(ast)
        temp = tempfile.NamedTemporaryFile()
        instrumented = self.generator.visit(ast)
        temp.write(bytes(instrumented, 'utf-8'))
        temp.flush()
        utils.preserve_include_postprocess(temp.name)
        out_path = join(tempfile.gettempdir(), "censor_out")
        return _compile_c(temp.name, self.includes, self.add_flags, out_path)


    def test_all(self):
        '''Assert instrumented code compiles'''
        for fixture in get_fixtures(self.fixtures):
            print('Testing instrumenter with ' + fixture)
            res = self.run_compilation(fixture)
            if res.returncode != 0:
                out = res.stderr.decode('utf-8')
                out_path = 'instrumenter_errors.txt'
                with open(out_path, 'w') as error_fd:
                    error_fd.write(out)
                raise self.failureException(out)
