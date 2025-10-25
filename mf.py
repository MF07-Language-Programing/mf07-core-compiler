"""MF command-line interface.

Provides subcommands to run scripts, build packages, produce standalone executables
and compile a subset of .mp to C (using tools/compile_to_c.py). The CLI executes
the existing helper scripts where needed and tries to be cross-platform.

Usage examples:
  mf run examples/first_project/main.mp
  mf compile-c examples/first_project/simple_example.mp -o generated.c --gcc-output myprog
  mf build-exe
  mf package --platform linux
  mf exec-compiled dist/mf
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import traceback
from typing import List, Optional


def run_script(path: str, ignore_type_errors: bool = False) -> int:
    # Use existing facade module to run
    try:
        from module import CorpLang
    except Exception as e:
        print(f"Erro ao importar runtime: {e}")
        return 2

    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return 2

    try:
        CorpLang(strict_types=not ignore_type_errors).run_file(path)
        return 0
    except Exception as e:
        print(f"Erro durante execução: {e}")
        return 1


def build_wheel() -> int:
    # run python -m build --wheel
    py = sys.executable
    cmd = [py, "-m", "build", "--wheel"]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


def build_exe() -> int:
    # Call platform-specific build script
    sysname = platform.system()
    if sysname == "Windows":
        script = os.path.join("scripts", "build_windows.bat")
        if not os.path.exists(script):
            print("Windows build script not found:", script)
            return 2
        return subprocess.call([script], shell=True)
    elif sysname == "Linux":
        script = os.path.join("scripts", "build_linux.sh")
        return subprocess.call(["bash", script])
    elif sysname == "Darwin":
        script = os.path.join("scripts", "build_macos.sh")
        return subprocess.call(["bash", script])
    else:
        print("Unsupported OS for build-exe:", sysname)
        return 3


def compile_to_c(input_mp: str, output_c: str, gcc_out: Optional[str] = None) -> int:
    py = sys.executable
    if not os.path.exists(input_mp):
        print("Input file not found:", input_mp)
        return 2

    cmd: List[str] = [
        py,
        os.path.join("tools", "compile_to_c.py"),
        input_mp,
        "-o",
        output_c,
    ]
    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        return rc

    if gcc_out:
        gcc = shutil.which("gcc")
        if not gcc:
            print("gcc not found in PATH; cannot compile C to binary")
            return 4
        print(f"Compiling {output_c} to {gcc_out} with gcc")
        rc2 = subprocess.call([gcc, "-O2", output_c, "-o", gcc_out])
        return rc2

    return 0


def package(platform_name: Optional[str] = None) -> int:
    # Call packaging helpers based on platform_name or auto-detect
    if platform_name is None:
        platform_name = platform.system().lower()

    if "win" in platform_name or platform_name == "windows":
        script = os.path.join("scripts", "package_windows.bat")
        if not os.path.exists(script):
            print("Windows packaging script missing")
            return 2
        return subprocess.call([script], shell=True)
    elif "linux" in platform_name:
        script = os.path.join("scripts", "package_linux.sh")
        if not os.path.exists(script):
            print("Linux packaging script missing")
            return 2
        return subprocess.call(["bash", script])
    elif "darwin" in platform_name or "mac" in platform_name:
        script = os.path.join("packaging", "package_macos.sh")
        if not os.path.exists(script):
            print("macOS packaging script missing")
            return 2
        return subprocess.call(["bash", script, os.path.join("dist", "mf")])
    else:
        print("Unknown platform for packaging:", platform_name)
        return 3


def exec_compiled(path: str, args: Optional[List[str]] = None) -> int:
    if not os.path.exists(path):
        print("Compiled file not found:", path)
        return 2
    cmd = [path]
    if args:
        cmd += args
    print("Executing:", " ".join(cmd))
    return subprocess.call(cmd)


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="mf", description="MF language CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run", help="Execute a .mp script")
    p_run.add_argument("path", help="Path to .mp file")
    p_run.add_argument("--ignore-type-errors", action="store_true")

    p_build_wheel = sub.add_parser(
        "build-wheel", help="Build a wheel via python -m build"
    )

    p_build_exe = sub.add_parser(
        "build-exe", help="Build a standalone executable with PyInstaller"
    )

    p_compile = sub.add_parser(
        "compile-c", help="Transpile .mp to C and optionally compile"
    )
    p_compile.add_argument("input", help="Input .mp file")
    p_compile.add_argument(
        "-o", "--output", default="generated.c", help="C output file"
    )
    p_compile.add_argument(
        "--gcc-output", help="If provided, run gcc to generate binary with this name"
    )

    p_package = sub.add_parser(
        "package", help="Create platform installer from built binary"
    )
    p_package.add_argument(
        "--platform", help="Target platform (windows, linux, mac) - defaults to current"
    )

    p_exec = sub.add_parser("exec-compiled", help="Execute a compiled binary")
    p_exec.add_argument("path", help="Path to compiled binary")
    p_exec.add_argument(
        "--args", nargs=argparse.REMAINDER, help="Arguments to pass to compiled binary"
    )

    p_version = sub.add_parser("version", help="Show version (from pyproject)")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        return run_script(args.path, ignore_type_errors=args.ignore_type_errors)
    if args.cmd == "build-wheel":
        return build_wheel()
    if args.cmd == "build-exe":
        return build_exe()
    if args.cmd == "compile-c":
        return compile_to_c(args.input, args.output, gcc_out=args.gcc_output)
    if args.cmd == "package":
        return package(args.platform)
    if args.cmd == "exec-compiled":
        return exec_compiled(args.path, args.args)
    if args.cmd == "version":
        # Try to read pyproject.toml simple
        try:
            import tomllib as tl
        except Exception:
            try:
                import toml as tl
            except Exception:
                tl = None
        if tl:
            try:
                with open("pyproject.toml", "r", encoding="utf-8") as f:
                    data = tl.load(f)
                ver = data.get("tool", {}).get("poetry", {}).get("version") or data.get(
                    "project", {}
                ).get("version")
                print(ver or "(version not found)")
            except Exception:
                print("(failed to read version)")
        else:
            print("toml library not available to read version")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
