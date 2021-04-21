import base64
from snippeteer.parse.source_file import SourceFile


def try_parse(content):
    """Attempt to parse a source file, return None if unsuccessful."""
    try:
        code = base64.b64decode(content).decode("utf-8")
    except:
        return None
    try:
        return SourceFile.from_code(code)
    except NotImplementedError as e:
        problems.append(e.args[0])
        return None
    except SyntaxError:
        return None
    except RecursionError:
        return None


problems = []
