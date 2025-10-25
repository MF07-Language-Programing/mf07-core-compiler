import os
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter


def parse_program(src_text):
    lex = Lexer(src_text)
    tokens = lex.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def test_parser_docstrings():
    src = '"module doc"\n\nintent myfn() {\n    "fn doc"\n    return 1\n}\n\nclass C {\n    intent m() {\n        "m doc"\n        return 2\n    }\n}\n\nvar f = fn() {\n    "lambda doc"\n    return 3\n}\n'
    program = parse_program(src)
    # module docstring
    assert getattr(program, "docstring", None) is not None
    # find function declaration
    fdecls = [s for s in program.statements if hasattr(s, "name") and s.name == "myfn"]
    assert fdecls, "myfn not found"
    fdecl = fdecls[0]
    assert getattr(fdecl, "docstring", None) == "fn doc"
    # class and method
    classes = [s for s in program.statements if hasattr(s, "name") and s.name == "C"]
    assert classes, "class C not found"
    cls = classes[0]
    methods = [m for m in cls.body if hasattr(m, "name") and m.name == "m"]
    assert methods, "method m not found"
    assert getattr(methods[0], "docstring", None) == "m doc"
    # lambda
    lambdas = [
        s
        for s in program.statements
        if hasattr(s, "value") and hasattr(s.value, "docstring")
    ]
    assert lambdas, "lambda assignment not found"
    lam = lambdas[0].value
    assert getattr(lam, "docstring", None) == "lambda doc"


def test_interpreter_docs_registry(tmp_path, monkeypatch):
    # write a temp core file and load with interpreter to exercise registry
    core_src = '"module core"\n\nintent core_fn() {\n    "core fn doc"\n}\n'
    core_dir = tmp_path / "core"
    core_dir.mkdir()
    core_file = core_dir / "tempcore.mp"
    core_file.write_text(core_src, encoding="utf-8")

    interp = Interpreter()
    # point interpreter to the temp core dir
    interp.load_core_modules(core_dir=str(core_dir))
    # registry should have core_fn
    assert "core_fn" in interp.docs
    assert interp.docs["core_fn"]["doc"] == "core fn doc"
