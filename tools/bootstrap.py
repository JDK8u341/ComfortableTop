"""Install pinned library wheels, the app, and optional independently built runtime."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TUI_REVISION = "e25f1f62c26ec99684f5b6e0ba1cf472930665f2"
TUI_URL = "https://github.com/JDK8u341/ComfortableTUI.git"


def run(*arguments, env=None):
    subprocess.run([str(a) for a in arguments], check=True, env=env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tui-source", type=Path, help="Use an explicit local dependency source without changing it")
    parser.add_argument("--terminal-only", action="store_true", help="Skip C++ and GUI dependencies")
    parser.add_argument("--gpu", action="store_true", help="Build ComfortableTUI's optional Windows GPU extension")
    parser.add_argument("--browser-runtime", type=Path)
    parser.add_argument("--host-binary", type=Path)
    parser.add_argument("--cef-root", type=Path)
    args = parser.parse_args()
    if args.gpu and (os.name != "nt" or args.terminal_only):
        parser.error("--gpu requires Windows native/hybrid setup")
    source = args.tui_source.resolve() if args.tui_source else ROOT / ".deps" / "comfortable-tui-src"
    if not args.tui_source:
        if not source.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            run("git", "clone", "--no-checkout", TUI_URL, source)
            run("git", "-C", source, "checkout", "--detach", TUI_REVISION)
        revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        if revision != TUI_REVISION:
            raise RuntimeError("Cached dependency has a different revision; supply an explicit --tui-source")
    if not (source / "pyproject.toml").is_file():
        parser.error("ComfortableTUI dependency source not found")
    run(sys.executable, "-m", "pip", "install", "setuptools>=77", "wheel", "build", "pybind11>=2.13")
    environment = os.environ.copy()
    environment.pop("COMFORTABLE_TUI_BUILD_GPU", None)
    environment.pop("COMFORTABLE_TUI_BUILD_NATIVE", None)
    if args.gpu:
        environment["COMFORTABLE_TUI_BUILD_GPU"] = "1"
    wheels = ROOT / ".deps" / ("gpu-wheels" if args.gpu else "wheels")
    wheels.mkdir(parents=True, exist_ok=True)
    run(sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--wheel-dir", wheels,
        source, env=environment)
    candidates = sorted(wheels.glob("comfortable_tui-*.whl"), key=lambda p: p.stat().st_mtime)
    run(sys.executable, "-m", "pip", "install", "--force-reinstall", candidates[-1])
    extras = "[dev,docs,overlay]" if os.name == "nt" and not args.terminal_only else "[dev,docs]"
    run(sys.executable, "-m", "pip", "install", "-e", str(ROOT) + extras)
    if not args.terminal_only:
        arguments = [sys.executable, ROOT / "tools" / "build_runtime.py", "--tui-source", source]
        for flag in ("browser_runtime", "host_binary", "cef_root"):
            value = getattr(args, flag)
            if value:
                arguments += ["--" + flag.replace("_", "-"), value.resolve()]
        run(*arguments)
    print("Ready: comfortable-top" + (" --mode hybrid" if args.browser_runtime or args.cef_root else ""))


if __name__ == "__main__":
    main()
