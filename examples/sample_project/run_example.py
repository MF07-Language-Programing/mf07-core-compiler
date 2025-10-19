import sys
from pathlib import Path

from module import CorpLang

def main():
    repo_root = Path(__file__).resolve().parents[2]
    example = repo_root / 'examples' / 'sample_project' / 'main.mp'
    lang = CorpLang()
    lang.run_file(str(example))

if __name__ == '__main__':
    main()
