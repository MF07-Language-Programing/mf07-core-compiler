from module import CorpLang
import pytest


def test_runtime_type_error_on_var_declaration():
    src = """
intent getClientName() : int {
    return "John Doe";
}

var name: int = getClientName();
"""
    lang = CorpLang()
    with pytest.raises(Exception):
        lang.run(src)
