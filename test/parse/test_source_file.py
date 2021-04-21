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
                keywords=frozenset(
                    {"normalize", "vector", "np", "numpy", "sqrt", "sum"}
                ),
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


def test_multiple_functions():
    code = """
import numpy as np

def normalize(vector):
    return vector / length(vector)

def length(vector):
    return np.sqrt(np.sum(vector ** 2))
"""
    assert SourceFile.from_code(code) == SourceFile(
        imports=Imports(modules={Imports.Alias(original="numpy", renamed="np")}),
        functions={
            Function(
                name="normalize",
                keywords=frozenset({"normalize", "vector", "length"}),
                docstring=None,
                arguments=("vector",),
                returns=frozenset(),
                dependencies=frozenset(),
                num_operations=3,
                first_line=3,
                last_line=5,
            ),
            Function(
                name="length",
                keywords=frozenset({"length", "vector", "np", "numpy", "sqrt", "sum"}),
                docstring=None,
                arguments=("vector",),
                returns=frozenset(),
                dependencies=frozenset({"numpy"}),
                num_operations=4,
                first_line=6,
                last_line=8,
            ),
        },
    )


def test_try_except():
    code = """
try:
    def f(): pass
except:
    def g(): pass
"""
    assert SourceFile.from_code(code) == SourceFile(
        imports=Imports(),
        functions={
            Function(
                name="f",
                keywords=frozenset({"f"}),
                docstring=None,
                arguments=(),
                returns=frozenset(),
                dependencies=frozenset(),
                num_operations=1,
                first_line=2,
                last_line=3,
            ),
            Function(
                name="g",
                keywords=frozenset({"g"}),
                docstring=None,
                arguments=(),
                returns=frozenset(),
                dependencies=frozenset(),
                num_operations=1,
                first_line=4,
                last_line=5,
            ),
        },
    )
