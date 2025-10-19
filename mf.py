import sys
from module import CorpLang


def main():
    if len(sys.argv) < 2:
        print("Usage: mf <script.mp> [--ignore-type-errors]")
        sys.exit(1)

    ignore_types = False
    filename = None
    for arg in sys.argv[1:]:
        if arg == "--ignore-type-errors":
            ignore_types = True
        elif filename is None:
            filename = arg
        else:
            print("Unexpected extra argument:", arg)
            sys.exit(1)

    if filename is None:
        print("Usage: mf <script.mp> [--ignore-type-errors]")
        sys.exit(1)

    CorpLang(strict_types=not ignore_types).run_file(filename)


if __name__ == "__main__":
    main()
