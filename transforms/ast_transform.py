"""Base ASTTransform class that every transform implements"""

class ASTTransform(): #pylint: disable=too-few-public-methods
    """Base abstract ASTTransform class"""

    def transform(self, node):
        """Override this method"""
        raise NotImplementedError(self.__class__.__name__ + " should not be used")
