import subprocess
import sys
from pathlib import Path


def test_example_runs_and_outputs_expected_lines(capsys):
    repo_root = Path(__file__).resolve().parents[1]
    example_bat = repo_root / 'examples' / 'sample_project' / 'run_example.bat'
    out_file = repo_root / 'examples' / 'sample_project' / 'run_output_test.txt'
    # Run the example and capture output
    # Run example in-process to avoid subprocess environment issues
    from module import CorpLang
    # Run example via the venv Python to isolate environment
    # Invoke the venv python directly to avoid shell quoting issues
    venv_py = repo_root / 'env' / 'Scripts' / 'python.exe'
    script = repo_root / 'examples' / 'sample_project' / 'run_example.py'
    # Run Python and insert repo_root into sys.path so 'module' can be imported
    runner = (
        "import sys;"
        f"sys.path.insert(0, r'{str(repo_root)}');"
        "from examples.sample_project.run_example import main;"
        "main()"
    )
    proc = subprocess.run([str(venv_py), '-c', runner], cwd=str(repo_root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.stdout.decode('utf-8', errors='replace')
    # Basic expected pieces
    assert 'Async sum result: 30' in output
    assert "Dataset 'users' carregado" in output
    assert "Modelo 'clf' treinado" in output
    assert 'Obj:' in output
