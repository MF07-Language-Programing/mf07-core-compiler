import sys
from pathlib import Path
repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))
from runtime.type_checker import check_source
p = repo / 'examples' / 'sample_project' / 'main.mp'
s = p.read_text(encoding='utf-8')
try:
    errs = check_source(s)
    print('Errors:', errs)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception:', e)
