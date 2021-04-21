from typing import Tuple, FrozenSet, Union
from dataclasses import dataclass
from itertools import chain
from functools import reduce, cached_property
import ast
from .imports import Imports
from .names import split_name
from .ast_utils import descend, leaf_types, extract_names, extract_line_numbers


@dataclass(frozen=True)
class Function:
    name: str
    keywords: FrozenSet[str]
    docstring: Union[str, None]
    arguments: Tuple[str]
    returns: FrozenSet[str]
    dependencies: FrozenSet[str]
    # side_effects: bool TODO - maybe just check if uses the global keyword?
    num_operations: int
    first_line: int
    last_line: int

    @classmethod
    def from_ast(cls, imports: Imports, function_def: ast.FunctionDef):
        try:
            docstring = function_def.body[0].value.s
        except AttributeError:
            docstring = None

        variables = frozenset(
            descend(function_def, handlers={ast.Name: lambda name: [name.id]})
        )  # intentionally descending whole function (not just body) to also get decorators

        dependencies = (
            reduce(
                frozenset.union,
                [imports.name_modules(variable) for variable in variables],
                frozenset(),
            )
            - frozenset({None})
        )
        line_numbers = extract_line_numbers(function_def)

        return cls(
            name=function_def.name,
            keywords=frozenset(
                keyword
                for name in chain(
                    extract_names(function_def),
                    dependencies,
                )
                for keyword in split_name(name)
            ),
            docstring=docstring,
            arguments=tuple(
                arg.arg
                for arg in chain(
                    function_def.args.posonlyargs,
                    function_def.args.args,
                    [function_def.args.vararg],
                    function_def.args.kwonlyargs,
                    [function_def.args.kwarg],
                )
                if arg is not None
            ),
            returns=frozenset(
                descend(
                    function_def.body, handlers={ast.Return: extract_returned_names}
                )
            ),
            dependencies=dependencies,
            num_operations=descend(
                function_def.body,
                handlers={node_type: lambda node: 1 for node_type in leaf_types},
                combiner=int.__add__,
                initial=0,
            ),
            first_line=min(line_numbers) - 1,  # numbering starts from 1
            last_line=max(line_numbers),
        )


def extract_returned_names(return_statement: ast.Return):
    try:
        return [return_statement.value.id]
    except NameError:
        return []
    except AttributeError:
        return []
