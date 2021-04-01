import ast
from snippeteer.parse.imports import Imports


def test_alias():
    code = "import numpy as np"
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code) == Imports(
        modules={Imports.Alias(original="numpy", renamed="np")}
    )


def test_from():
    code = """
from sklearn.tree import DecisionTreeClassifier, SomethingElse as SE
    """
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code) == Imports(
        variables={
            "sklearn.tree": {
                Imports.Alias(
                    original="DecisionTreeClassifier", renamed="DecisionTreeClassifier"
                ),
                Imports.Alias(original="SomethingElse", renamed="SE"),
            }
        }
    )


def test_multiline():
    code = """
import cv2
import numpy as np
from sklearn.tree import DecisionTreeClassifier as TC

def function(arg):
    return arg + 1
    """
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code) == Imports(
        modules={
            Imports.Alias(original="cv2", renamed="cv2"),
            Imports.Alias(original="numpy", renamed="np"),
        },
        variables={
            "sklearn.tree": {
                Imports.Alias(original="DecisionTreeClassifier", renamed="TC")
            }
        },
    )


def test_nested():
    code = """
def function(arg):
    import sneaky_import
    return arg + 1
    """
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code) == Imports(
        modules={Imports.Alias(original="sneaky_import", renamed="sneaky_import")}
    )


def test_name_modules():
    code = """
import numpy as np
from cv2 import secret
    """
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code).name_modules("np") == {"numpy"}
    assert Imports.from_ast(parsed_code).name_modules("secret") == {"cv2"}
    assert Imports.from_ast(parsed_code).name_modules("not_imported") == set()


def test_unequal():
    code = "def x(): pass"
    parsed_code = ast.parse(code, mode="exec")
    assert Imports.from_ast(parsed_code) != Imports(
        modules={Imports.Alias(original="numpy", renamed="np")}
    )
    assert not Imports.from_ast(parsed_code) == Imports(
        modules={Imports.Alias(original="numpy", renamed="np")}
    )
