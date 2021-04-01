import ast
from snippeteer.parse.imports import Imports
from snippeteer.parse.function import Function


def test_tiny():
    code = "def f(arg): pass"
    parsed_code = ast.parse(code, mode="exec")
    assert Function.from_ast(
        imports=Imports(), function_def=parsed_code.body[0]
    ) == Function(
        name="f",
        docstring=None,
        arguments=("arg",),
        returns=set(),
        dependencies=set(),
        num_operations=1,
        first_line=0,
        last_line=1,
    )


def test_return_names():
    code = """
def f(arg):
    return x
    return y
    """
    parsed_code = ast.parse(code, mode="exec")
    assert Function.from_ast(
        imports=Imports(), function_def=parsed_code.body[0]
    ) == Function(
        name="f",
        docstring=None,
        arguments=("arg",),
        returns={"x", "y"},
        dependencies=set(),
        num_operations=2,
        first_line=1,
        last_line=4,
    )


def test_imports():
    code = "def f(arg): return np.square(arg)"
    parsed_code = ast.parse(code, mode="exec")
    assert Function.from_ast(
        imports=Imports(modules={Imports.Alias(original="numpy", renamed="np")}),
        function_def=parsed_code.body[0],
    ) == Function(
        name="f",
        docstring=None,
        arguments=("arg",),
        returns=set(),
        dependencies={"numpy"},
        num_operations=2,
        first_line=0,
        last_line=1,
    )
