from typing import Set, Dict
from functools import cached_property
import ast
import attr
from .ast_utils import descend


@attr.s(auto_attribs=True)
class Imports:
    @attr.s(auto_attribs=True, hash=True)
    class Alias:
        original: str
        renamed: str

        @classmethod
        def from_ast(cls, ast_node: ast.alias):
            if ast_node.asname is None:
                return cls(original=ast_node.name, renamed=ast_node.name)
            return cls(original=ast_node.name, renamed=ast_node.asname)

    modules: Set[Alias] = set()
    variables: Dict[str, Set[Alias]] = {}

    @classmethod
    def from_ast(cls, ast_node):
        return descend(
            ast_node,
            handlers={
                ast.Import: cls.from_import_statement,
                ast.ImportFrom: cls.from_import_from_statement,
            },
            combiner=cls.__or__,
            initial=cls(),
        )

    @classmethod
    def from_import_statement(cls, import_statement: ast.Import):
        return cls(
            modules={cls.Alias.from_ast(alias) for alias in import_statement.names},
        )

    @classmethod
    def from_import_from_statement(cls, import_from_statement: ast.ImportFrom):
        return cls(
            variables={
                import_from_statement.module: cls.Alias.from_ast(alias)
                for alias in import_from_statement.names
            },
        )

    @cached_property
    def names(self):
        return set(module.renamed for module in self.modules) | set(
            variable.renamed
            for variables in self.variables.values()
            for variable in variables
        )

    def __or__(self, other):
        return type(self)(
            modules=self.modules | other.modules,
            variables={**self.variables, **other.variables},
        )
