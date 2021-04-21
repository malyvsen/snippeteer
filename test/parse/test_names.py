from snippeteer.parse.names import split_name


def test_camel_case():
    assert split_name("CamelCase") == ["camel", "case"]
    assert split_name("shyCamelCase") == ["shy", "camel", "case"]
    assert split_name("CamelIdCase") == ["camel", "id", "case"]
    assert split_name("CamelIDCase") == ["camel", "id", "case"]
    assert split_name("CamelCaseID") == ["camel", "case", "id"]


def test_snake_case():
    assert split_name("snake_case") == ["snake", "case"]
    assert split_name("__dunder__") == ["dunder"]


def test_mixed_case():
    assert split_name("WigglySnake_case") == ["wiggly", "snake", "case"]
