from typing import List, Set, Union
from itertools import chain
from functools import reduce
import ast
import attr
from .imports import Imports
from .ast_utils import descend, node_children


@attr.s(auto_attribs=True)
class Function:
    name: str
    docstring: Union[str, None]
    arguments: List[str]
    returns: List[str]
    dependencies: Set[str]
    # side_effects: bool  # TODO
    num_operations: int
    first_line: int
    last_line: int

    @classmethod
    def from_ast(cls, imports: Imports, function_def: ast.FunctionDef):
        try:
            docstring = function_def.body[0].value.s
        except AttributeError:
            docstring = None

        used_variables = descend(
            function_def, handlers={ast.Name: lambda name: [name.id]}
        )  # intentionally descending whole function (not just body) to also get decorators
        # TODO: cv2 = 3 will count as using the cv2 module (it shouldn't)

        leaf_node_types = [
            node_type
            for node_type, children in node_children.items()
            if len(children) == 0
            if not isinstance(None, node_type)
        ]

        return cls(
            name=function_def.name,
            docstring=docstring,
            arguments=[
                arg.arg
                for arg in chain(
                    function_def.args.posonlyargs,
                    function_def.args.args,
                    [function_def.args.vararg],
                    function_def.args.kwonlyargs,
                    [function_def.args.kwarg],
                )
                if arg is not None
            ],
            returns=descend(
                function_def.body, handlers={ast.Return: extract_returned_names}
            ),
            dependencies=reduce(
                set.union,
                [imports.name_modules(variable) for variable in used_variables],
                set(),
            ),
            num_operations=descend(
                function_def.body,
                handlers={node_type: lambda node: 1 for node_type in leaf_node_types},
                combiner=int.__add__,
                initial=0,
            ),
            first_line=descend(
                function_def,
                handlers={
                    node_type: lambda node: node.lineno for node_type in leaf_node_types
                },
                combiner=min,
                initial=float("inf"),
            )
            - 1,  # numbering starts from 1
            last_line=descend(
                function_def,
                handlers={
                    node_type: lambda node: node.lineno for node_type in leaf_node_types
                },
                combiner=max,
                initial=float("-inf"),
            ),
        )


def extract_returned_names(return_statement: ast.Return):
    try:
        return [return_statement.value.id]
    except NameError:
        return []
    except AttributeError:
        return []
