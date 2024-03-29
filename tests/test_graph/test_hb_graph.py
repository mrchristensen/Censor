"""Test HBGraph"""

from tests.helpers import GoldenTestCase
from graph.hb_graph import HBGraph

def build_graph(log):
    """Build graph from log file. Print graph"""
    hb_graph = HBGraph()
    hb_graph.from_log_file(log)
    return "%s" % (hb_graph)

class TestHBGraph(GoldenTestCase):
    """TestHBGraph"""

    def setUp(self): #pylint: disable=invalid-name
        """Set up test cases"""
        self.fixtures = '/test_graph/fixtures/hb_graph'

    def test_fixtures(self):
        """Test all fixtures"""
        self.assert_all_golden(build_graph, self.fixtures)
