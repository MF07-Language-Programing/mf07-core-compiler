from runtime.type_checker import check_source


def test_var_type_mismatch():
    src = 'var x: int = "hello";'
    errs = check_source(src)
    assert len(errs) == 1
    assert "Type mismatch for variable" in str(errs[0])


def test_function_return_mismatch():
    src = 'intent f(): int {\n    return "oops";\n}\n'
    errs = check_source(src)
    assert len(errs) == 1
    assert "Return type mismatch" in str(errs[0])


def test_no_errors_happy_path():
    src = "var a: int = 1;\nintent g(): int {\n    return 2;\n}\n"
    errs = check_source(src)
    assert len(errs) == 0


def test_call_argument_mismatch():
    src = "intent f(a: int, b: string){\n    return 1;\n}\n" 'f("hello", 2);\n'
    errs = check_source(src)
    # Expect at least one argument type mismatch
    assert any("Argument type mismatch" in str(e) for e in errs)


def test_call_argument_happy():
    src = "intent add(a: int, b: int): int {\n    return a + b;\n}\n" "add(1, 2);\n"
    errs = check_source(src)
    assert len(errs) == 0
