import ast
from snippeteer.parse.ast_utils import extract_names


def test_snippet():
    code = """
import numpy as np

def normalize(vector):
    return vector / np.square(vector).sum()
    """
    parsed_code = ast.parse(code, mode="exec")
    assert extract_names(parsed_code) == {
        "numpy",
        "np",
        "normalize",
        "vector",
        "vector",
        "np",
        "square",
        "vector",
        "sum",
    }
