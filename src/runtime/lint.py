import sys

from .type_checker import check_source


def main():
    if len(sys.argv) < 2:
        print("Usage: python lint.py <file.mp>")
        return 1
    fn = sys.argv[1]
    try:
        with open(fn, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"File '{fn}' not found")
        return 2

    errors = check_source(src)
    if not errors:
        print("Lint OK: no type errors")
        return 0
    for err in errors:
        print("Error:", err)
    return 3


if __name__ == "__main__":
    sys.exit(main())
