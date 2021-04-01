import ast
from snippeteer.parse.imports import Imports
from snippeteer.parse.function import Function
from snippeteer.parse.source_file import SourceFile


def test_short():
    code = """
import numpy as np

def normalize(vector):
    return vector / np.sqrt(np.sum(vector ** 2))
"""
    assert SourceFile.from_code(code) == SourceFile(
        imports=Imports(modules={Imports.Alias(original="numpy", renamed="np")}),
        functions={
            Function(
                name="normalize",
                docstring=None,
                arguments=("vector",),
                returns=frozenset(),
                dependencies=frozenset({"numpy"}),
                num_operations=5,
                first_line=3,
                last_line=5,
            )
        },
    )
