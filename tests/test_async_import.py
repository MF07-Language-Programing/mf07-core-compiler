import os
from module import CorpLang


def test_async_await(capsys):
    executor = CorpLang()
    executor.run_file(os.path.join("tests", "mf_test", "async_test.mp"))
    captured = capsys.readouterr()
    assert "ASYNC_RESULT: 5" in captured.out or "5" in captured.out


def test_import(capsys):
    executor = CorpLang()
    executor.run_file(os.path.join("tests", "mf_test", "import_test_main.mp"))
    captured = capsys.readouterr()
    assert "IMPORTED: 42" in captured.out or "42" in captured.out
