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
    except NotImplementedError:
        return None
    except SyntaxError:
        return None
    except Exception as e:
        print(code)
        raise e
