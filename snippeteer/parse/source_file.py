from typing import FrozenSet
from dataclasses import dataclass
import ast
from .ast_utils import descend
from .imports import Imports
from .function import Function


@dataclass
class SourceFile:
    imports: Imports
    functions: FrozenSet[Function]

    @classmethod
    def from_code(cls, code: str):
        return cls.from_ast(ast.parse(code, mode="exec"))

    @classmethod
    def from_ast(cls, ast_node):
        imports = Imports.from_ast(ast_node)
        return cls(
            imports=imports,
            functions=descend(
                ast_node,
                handlers={
                    ast.FunctionDef: lambda function_node: frozenset(
                        {Function.from_ast(imports=imports, function_def=function_node)}
                    )
                },
                combiner=frozenset.union,
                initial=frozenset(),
            ),
        )
