import importlib.util
import sys
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'corp-lang-vscode' / 'client' / 'server.py'
print('checking', p)
spec = importlib.util.spec_from_file_location('corp_lang_server', str(p))
if spec is None:
    print('failed to create module spec for', p)
    sys.exit(2)
mod = importlib.util.module_from_spec(spec)
try:
    loader = getattr(spec, "loader", None)
    if loader is None or not hasattr(loader, "exec_module"):
        print('no module loader (or exec_module missing) for', p)
        sys.exit(2)
    loader.exec_module(mod)
    print('import_ok')
except Exception as e:
    print('import_error')
    import traceback
    traceback.print_exc()
    sys.exit(2)
