'''Customized OMP Node code generator.
    Grants us the ability to add a property to all Nodes.
'''

#pylint: disable=too-few-public-methods,bad-continuation,super-init-not-called

from pycparser._ast_gen import ASTCodeGenerator, NodeCfg

class OmpASTCodeGenerator(ASTCodeGenerator):
    '''Customized OmpNode Generation class'''
    def __init__(self, cfg_filename='_c_ast.cfg'):
        '''Initialize the code generator from a configuration
            file.
            This code is identical to the original init with the exception of
            the node_cfg is a OmpNodeCfg instead of the original NodeCfg.'''
        self.cfg_filename = cfg_filename
        self.node_cfg = [OmpNodeCfg(name, contents)
            for (name, contents) in self.parse_cfgfile(cfg_filename)]



class OmpNodeCfg(NodeCfg):
    '''Custom NodeCfg class for inserting another property into all nodes'''
    def __init__(self, name, contents):
        '''Node configuration. This one will also insert a child node called
            pragma to each Omp node.

            name: node name
            contents: a list of contents - attributes and child nodes
            See comment at the top of the configuration file for details.'''
        super().__init__(name, contents)
        self.attr.insert(0, "pragma")
        self.all_entries.insert(0, "pragma")
